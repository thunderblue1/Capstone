"""TC-13 and TC-28: Stripe payment and webhook tests."""
from unittest.mock import MagicMock, patch

import stripe
from models import Order, db


def test_tc13_stripe_payment_intent(client, customer_auth, seed_data):
    """TC-13: Stripe config, create intent, and confirm payment flow (mocked)."""
    config_response = client.get('/api/orders/stripe/config')
    assert config_response.status_code == 200
    assert 'publishableKey' in config_response.get_json()

    book_id = seed_data['fiction_book_id']
    items = [{'bookId': str(book_id), 'quantity': 1}]

    mock_intent = MagicMock()
    mock_intent.client_secret = 'cs_test_secret'
    mock_intent.id = 'pi_test_123'

    mock_customer_list = MagicMock()
    mock_customer_list.data = []

    with patch('routes.orders.stripe.Customer.list', return_value=mock_customer_list), \
         patch('routes.orders.stripe.Customer.create', return_value=MagicMock(id='cus_test')), \
         patch('routes.orders.stripe.PaymentIntent.create', return_value=mock_intent):
        intent_response = client.post(
            '/api/orders/stripe/create-intent',
            headers=customer_auth['headers'],
            json={
                'items': items,
                'customerEmail': 'test@example.com',
                'customerName': 'Test User',
            },
        )

    assert intent_response.status_code == 200
    intent_data = intent_response.get_json()
    assert intent_data['clientSecret'] == 'cs_test_secret'
    assert intent_data['paymentIntentId'] == 'pi_test_123'

    mock_payment_intent = MagicMock()
    mock_payment_intent.status = 'succeeded'
    mock_payment_intent.metadata = {'user_id': str(customer_auth['user']['id'])}
    mock_payment_intent.customer = 'cus_test'

    with patch('routes.orders.stripe.PaymentIntent.retrieve', return_value=mock_payment_intent):
        confirm_response = client.post(
            '/api/orders/stripe/confirm',
            headers=customer_auth['headers'],
            json={
                'paymentIntentId': 'pi_test_123',
                'items': items,
                'customerEmail': 'test@example.com',
                'customerName': 'Test User',
            },
        )

    assert confirm_response.status_code == 201
    order = confirm_response.get_json()['order']
    assert order['status'] == 'Paid'


def test_tc28_stripe_webhook_signature_rejects_bad(client, app):
    """TC-28: Webhook rejects invalid signature when secret is configured."""
    with patch(
        'routes.orders.stripe.Webhook.construct_event',
        side_effect=stripe.error.SignatureVerificationError('Invalid signature', sig_header='bad_sig'),
    ):
        response = client.post(
            '/api/orders/stripe/webhook',
            data='{"type":"payment_intent.succeeded"}',
            headers={'Stripe-Signature': 'bad_sig', 'Content-Type': 'application/json'},
        )

    assert response.status_code == 400


def test_tc28_stripe_webhook_accepts_valid_event(client, app):
    """TC-28: Webhook accepts valid signed event and updates order status."""
    with app.app_context():
        from tests.conftest import register_user

        user_response = register_user(client, username='stripeuser', email='stripe@example.com')
        user_id = user_response.get_json()['user']['id']

        order = Order(
            user_id=user_id,
            total_amount=19.99,
            status='Pending',
            stripe_payment_intent_id='pi_webhook_test',
        )
        db.session.add(order)
        db.session.commit()
        order_id = order.id

    mock_event = {
        'type': 'payment_intent.succeeded',
        'data': {'object': {'id': 'pi_webhook_test'}},
    }

    with patch('routes.orders.stripe.Webhook.construct_event', return_value=mock_event):
        response = client.post(
            '/api/orders/stripe/webhook',
            data='{"type":"payment_intent.succeeded"}',
            headers={'Stripe-Signature': 'valid_sig', 'Content-Type': 'application/json'},
        )

    assert response.status_code == 200

    with app.app_context():
        updated = Order.query.get(order_id)
        assert updated.status == 'Paid'
