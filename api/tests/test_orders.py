"""TC-11 through TC-15, TC-27: Orders API tests."""
from tests.conftest import create_order_for_user


def test_tc11_validate_cart(client, seed_data):
    """TC-11: POST /api/orders/cart/validate confirms stock and prices."""
    book = seed_data['fiction_book_id']
    response = client.post(
        '/api/orders/cart/validate',
        json={'items': [{'bookId': str(book), 'quantity': 2}]},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['valid'] is True
    assert data['subtotal'] > 0
    assert len(data['items']) == 1


def test_tc11_validate_cart_insufficient_stock(client, seed_data):
    """TC-11: Cart validation fails when stock is insufficient."""
    out_of_stock = seed_data['out_of_stock_book_id']
    response = client.post(
        '/api/orders/cart/validate',
        json={'items': [{'bookId': str(out_of_stock), 'quantity': 1}]},
    )

    data = response.get_json()
    assert data['valid'] is False
    assert data['errors']


def test_tc12_checkout_creates_order(client, customer_auth, seed_data):
    """TC-12: Checkout flow creates Pending order."""
    book_id = seed_data['fiction_book_id']
    response = client.post(
        '/api/orders/checkout',
        headers=customer_auth['headers'],
        json={'items': [{'bookId': str(book_id), 'quantity': 1}]},
    )

    assert response.status_code == 201
    order = response.get_json()['order']
    assert order['status'] == 'Pending'
    assert len(order['items']) == 1

    list_response = client.get('/api/orders', headers=customer_auth['headers'])
    orders = list_response.get_json()['orders']
    assert any(o['id'] == order['id'] for o in orders)


def test_tc14_list_orders_own_only(client, customer_auth, second_customer_auth, seed_data, app):
    """TC-14: GET /api/orders returns only the authenticated user's orders."""
    book_id = seed_data['fiction_book_id']
    create_order_for_user(app, customer_auth['user']['id'], book_id)
    create_order_for_user(app, second_customer_auth['user']['id'], book_id)

    response = client.get('/api/orders', headers=customer_auth['headers'])
    assert response.status_code == 200
    orders = response.get_json()['orders']
    assert len(orders) == 1
    assert orders[0]['userId'] == str(customer_auth['user']['id'])


def test_tc15_cancel_order(client, customer_auth, seed_data, app):
    """TC-15: Cancel own pending order sets status to Cancelled."""
    book_id = seed_data['fiction_book_id']
    order_id = create_order_for_user(app, customer_auth['user']['id'], book_id, status='Pending')

    response = client.post(
        f'/api/orders/{order_id}/cancel',
        headers=customer_auth['headers'],
    )

    assert response.status_code == 200
    assert response.get_json()['order']['status'] == 'Cancelled'


def test_tc15_cancel_non_pending_order_fails(client, customer_auth, seed_data, app):
    """TC-15: Cannot cancel order that is not Pending."""
    book_id = seed_data['fiction_book_id']
    order_id = create_order_for_user(app, customer_auth['user']['id'], book_id, status='Paid')

    response = client.post(
        f'/api/orders/{order_id}/cancel',
        headers=customer_auth['headers'],
    )

    assert response.status_code == 400


def test_tc27_customer_cannot_read_other_users_order(client, customer_auth, second_customer_auth, seed_data, app):
    """TC-27: GET /api/orders/<other_id> returns 403 for non-owner."""
    book_id = seed_data['fiction_book_id']
    other_order_id = create_order_for_user(app, second_customer_auth['user']['id'], book_id)

    response = client.get(
        f'/api/orders/{other_order_id}',
        headers=customer_auth['headers'],
    )

    assert response.status_code == 403
