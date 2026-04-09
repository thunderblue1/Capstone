"""
Orders API Routes Module (Checkout/Cart)
========================================

Purpose:
    Provides REST API endpoints for shopping cart validation and
    order management including checkout, payment processing, and
    order history.

Endpoints:
    GET  /api/orders                - Get user's order history (auth required)
    GET  /api/orders/<id>           - Get single order details (auth required)
    POST /api/orders/checkout       - Create order from cart (auth required)
    POST /api/orders/<id>/pay       - Mark order as paid (auth required)
    POST /api/orders/<id>/cancel    - Cancel pending order (auth required)
    POST /api/orders/cart/validate  - Validate cart items (no auth required)
    POST /api/orders/stripe/create-intent - Create Stripe payment intent (auth required)
    POST /api/orders/stripe/confirm - Confirm Stripe payment and create order (auth required)
    GET  /api/orders/stripe/config  - Get Stripe publishable key (no auth required)

Order Status Flow:
    Pending -> Paid -> Shipped -> Delivered
           \-> Cancelled (from Pending only)

Stock Management:
    - Stock is reduced when order is created (checkout)
    - Stock is restored when order is cancelled

Usage:
    Cart validation can be used without authentication for guest carts.
    All other endpoints require JWT authentication.

Dependencies:
    - Flask-JWT-Extended for authentication
    - models.Order, models.OrderItem, models.Book for data access
    - Stripe for payment processing
"""
import stripe
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc
from models import db, Order, OrderItem, Book
from utils.tax import calculate_tax

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """Get all orders for the current user"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = Order.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(desc(Order.created_at))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'orders': [order.to_dict() for order in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'currentPage': page
    })


@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get a single order by ID"""
    user_id = get_jwt_identity()
    order = Order.query.get_or_404(order_id)
    
    # Check ownership
    if str(order.user_id) != str(user_id):
        return jsonify({'error': 'Not authorized to view this order'}), 403
    
    return jsonify(order.to_dict(include_items=True))


@orders_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    """
    Create a new order from cart items.
    
    This is a transactional operation that:
    1. Validates all cart items exist and have sufficient stock
    2. Creates an Order record with 'Pending' status
    3. Creates OrderItem records for each cart item
    4. Reduces stock quantities for purchased books
    
    Request Body:
        {
            "items": [
                {"bookId": "123", "quantity": 2},
                {"bookId": "456", "quantity": 1}
            ]
        }
    
    Returns:
        201: Order created successfully with order details
        400: Invalid request (empty cart, missing bookId)
        404: Book not found
        400: Insufficient stock
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # ─────────────────────────────────────────────────────────────
    # INPUT VALIDATION: Ensure request has valid cart data
    # ─────────────────────────────────────────────────────────────
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    items = data.get('items', [])
    
    if not items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # ─────────────────────────────────────────────────────────────
    # CART VALIDATION: Verify each item exists and has stock
    # Build list of validated items with current prices
    # ─────────────────────────────────────────────────────────────
    order_items = []
    total_amount = 0
    
    for item in items:
        book_id = item.get('bookId')
        quantity = item.get('quantity', 1)
        
        # Validate bookId is provided
        if not book_id:
            return jsonify({'error': 'bookId is required for each item'}), 400
        
        # Fetch book from database
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'error': f'Book with id {book_id} not found'}), 404
        
        # Check stock availability
        if book.stock_quantity < quantity:
            return jsonify({
                'error': f'Insufficient stock for "{book.title}". Available: {book.stock_quantity}'
            }), 400
        
        # Calculate item subtotal using current price
        unit_price = float(book.price)
        subtotal = unit_price * quantity
        total_amount += subtotal
        
        order_items.append({
            'book': book,
            'quantity': quantity,
            'unit_price': unit_price
        })
    
    # ─────────────────────────────────────────────────────────────
    # ORDER CREATION: Create order record with pending status
    # ─────────────────────────────────────────────────────────────
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        currency='USD',
        status='Pending'
    )
    db.session.add(order)
    db.session.flush()  # Flush to get order.id before creating items
    
    # ─────────────────────────────────────────────────────────────
    # ORDER ITEMS: Create line items and update inventory
    # Stock reduction happens here to prevent overselling
    # ─────────────────────────────────────────────────────────────
    for item_data in order_items:
        order_item = OrderItem(
            order_id=order.id,
            book_id=item_data['book'].id,
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price']
        )
        db.session.add(order_item)
        
        # Reduce stock immediately to prevent race conditions
        item_data['book'].stock_quantity -= item_data['quantity']
    
    # Commit all changes in single transaction
    db.session.commit()
    
    return jsonify({
        'message': 'Order created successfully',
        'order': order.to_dict(include_items=True)
    }), 201


@orders_bp.route('/<int:order_id>/pay', methods=['POST'])
@jwt_required()
def pay_order(order_id):
    """Mark an order as paid (mock payment)"""
    user_id = get_jwt_identity()
    order = Order.query.get_or_404(order_id)
    
    # Check ownership
    if str(order.user_id) != str(user_id):
        return jsonify({'error': 'Not authorized to pay for this order'}), 403
    
    if order.status != 'Pending':
        return jsonify({'error': f'Order cannot be paid. Current status: {order.status}'}), 400
    
    # In a real app, you would process payment here
    # For now, just mark as paid
    order.status = 'Paid'
    db.session.commit()
    
    return jsonify({
        'message': 'Payment successful',
        'order': order.to_dict()
    })


@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order"""
    user_id = get_jwt_identity()
    order = Order.query.get_or_404(order_id)
    
    # Check ownership
    if str(order.user_id) != str(user_id):
        return jsonify({'error': 'Not authorized to cancel this order'}), 403
    
    if order.status not in ['Pending']:
        return jsonify({'error': f'Order cannot be cancelled. Current status: {order.status}'}), 400
    
    # Restore stock
    for item in order.items:
        item.book.stock_quantity += item.quantity
    
    order.status = 'Cancelled'
    db.session.commit()
    
    return jsonify({
        'message': 'Order cancelled successfully',
        'order': order.to_dict()
    })


@orders_bp.route('/cart/validate', methods=['POST'])
def validate_cart():
    """Validate cart items (check stock, prices) without creating an order"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    items = data.get('items', [])
    
    if not items:
        return jsonify({
            'valid': True,
            'items': [],
            'subtotal': 0,
            'tax': 0,
            'total': 0
        })
    
    validated_items = []
    subtotal = 0
    errors = []
    
    for item in items:
        book_id = item.get('bookId')
        quantity = item.get('quantity', 1)
        
        if not book_id:
            errors.append({'error': 'bookId is required for each item'})
            continue
        
        book = Book.query.get(book_id)
        if not book:
            errors.append({'bookId': book_id, 'error': 'Book not found'})
            continue
        
        item_valid = book.stock_quantity >= quantity
        item_subtotal = float(book.price) * quantity
        subtotal += item_subtotal
        
        validated_items.append({
            'bookId': str(book_id),
            'book': book.to_dict(),
            'quantity': quantity,
            'unitPrice': float(book.price),
            'subtotal': item_subtotal,
            'available': book.stock_quantity,
            'valid': item_valid
        })
        
        if not item_valid:
            errors.append({
                'bookId': book_id,
                'error': f'Insufficient stock. Available: {book.stock_quantity}'
            })
    
    tax = subtotal * 0.08  # 8% tax
    total = subtotal + tax
    
    return jsonify({
        'valid': len(errors) == 0,
        'items': validated_items,
        'subtotal': round(subtotal, 2),
        'tax': round(tax, 2),
        'total': round(total, 2),
        'errors': errors if errors else None
    })


@orders_bp.route('/stripe/config', methods=['GET'])
def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    publishable_key = current_app.config.get('STRIPE_PUBLISHABLE_KEY', '')
    return jsonify({
        'publishableKey': publishable_key
    })


@orders_bp.route('/stripe/create-intent', methods=['POST'])
@jwt_required()
def create_stripe_intent():
    """
    Create a Stripe Payment Intent for checkout.
    
    Request Body:
        {
            "items": [
                {"bookId": "123", "quantity": 2},
                {"bookId": "456", "quantity": 1}
            ],
            "customerEmail": "customer@example.com",
            "customerName": "John Doe",
            "shippingAddress": {
                "line1": "123 Main St",
                "line2": "Apt 4B",
                "city": "New York",
                "state": "NY",
                "postalCode": "10001",
                "country": "US"
            }
        }
    
    Returns:
        200: Payment intent created with client_secret
        400: Invalid request or insufficient stock
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    items = data.get('items', [])
    if not items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Validate cart and calculate total
    order_items = []
    total_amount = 0
    
    for item in items:
        book_id = item.get('bookId')
        quantity = item.get('quantity', 1)
        
        if not book_id:
            return jsonify({'error': 'bookId is required for each item'}), 400
        
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'error': f'Book with id {book_id} not found'}), 404
        
        if book.stock_quantity < quantity:
            return jsonify({
                'error': f'Insufficient stock for "{book.title}". Available: {book.stock_quantity}'
            }), 400
        
        unit_price = float(book.price)
        subtotal = unit_price * quantity
        total_amount += subtotal

    # Calculate tax based on state
    shipping_state = data.get('shippingAddress', {}).get('state')
    tax = calculate_tax(total_amount, shipping_state)
    total_amount += tax
    
    # Convert to cents for Stripe
    amount_in_cents = int(total_amount * 100)
    
    # Initialize Stripe
    stripe_secret_key = current_app.config.get('STRIPE_SECRET_KEY')
    if not stripe_secret_key:
        return jsonify({'error': 'Stripe not configured'}), 500
    
    stripe.api_key = stripe_secret_key
    
    # Get customer information
    customer_email = data.get('customerEmail')
    customer_name = data.get('customerName')
    
    # Create or retrieve Stripe customer
    stripe_customer = None
    if customer_email:
        try:
            # Try to find existing customer
            customers = stripe.Customer.list(email=customer_email, limit=1)
            if customers.data:
                stripe_customer = customers.data[0]
            else:
                # Create new customer
                stripe_customer = stripe.Customer.create(
                    email=customer_email,
                    name=customer_name,
                    metadata={'user_id': str(user_id)}
                )
        except stripe.error.StripeError as e:
            return jsonify({'error': f'Stripe customer error: {str(e)}'}), 500
    
    # Create payment intent
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency='usd',
            customer=stripe_customer.id if stripe_customer else None,
            metadata={
                'user_id': str(user_id),
                'order_type': 'book_purchase'
            },
            automatic_payment_methods={
                'enabled': True,
            },
        )
        
        return jsonify({
            'clientSecret': payment_intent.client_secret,
            'paymentIntentId': payment_intent.id,
            'amount': total_amount,
            'currency': 'usd'
        })
    except stripe.error.StripeError as e:
        return jsonify({'error': f'Stripe error: {str(e)}'}), 500


@orders_bp.route('/stripe/confirm', methods=['POST'])
@jwt_required()
def confirm_stripe_payment():
    """
    Confirm Stripe payment and create order.
    
    Request Body:
        {
            "paymentIntentId": "pi_xxx",
            "items": [
                {"bookId": "123", "quantity": 2},
                {"bookId": "456", "quantity": 1}
            ],
            "customerEmail": "customer@example.com",
            "customerName": "John Doe",
            "shippingAddress": {
                "line1": "123 Main St",
                "line2": "Apt 4B",
                "city": "New York",
                "state": "NY",
                "postalCode": "10001",
                "country": "US"
            }
        }
    
    Returns:
        201: Order created successfully
        400: Invalid request or payment failed
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    payment_intent_id = data.get('paymentIntentId')
    if not payment_intent_id:
        return jsonify({'error': 'paymentIntentId is required'}), 400
    
    items = data.get('items', [])
    if not items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Initialize Stripe
    stripe_secret_key = current_app.config.get('STRIPE_SECRET_KEY')
    if not stripe_secret_key:
        return jsonify({'error': 'Stripe not configured'}), 500
    
    stripe.api_key = stripe_secret_key
    
    # Verify payment intent
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if payment_intent.status != 'succeeded':
            return jsonify({
                'error': f'Payment not completed. Status: {payment_intent.status}'
            }), 400
        
        # Verify user matches
        if payment_intent.metadata.get('user_id') != str(user_id):
            return jsonify({'error': 'Payment intent does not belong to this user'}), 403
            
    except stripe.error.StripeError as e:
        return jsonify({'error': f'Stripe error: {str(e)}'}), 500
    
    # Validate cart items and calculate total
    order_items = []
    total_amount = 0
    
    for item in items:
        book_id = item.get('bookId')
        quantity = item.get('quantity', 1)
        
        if not book_id:
            return jsonify({'error': 'bookId is required for each item'}), 400
        
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'error': f'Book with id {book_id} not found'}), 404
        
        if book.stock_quantity < quantity:
            return jsonify({
                'error': f'Insufficient stock for "{book.title}". Available: {book.stock_quantity}'
            }), 400
        
        unit_price = float(book.price)
        subtotal = unit_price * quantity
        total_amount += subtotal
        
        order_items.append({
            'book': book,
            'quantity': quantity,
            'unit_price': unit_price
        })
    
    # Calculate tax based on state
    shipping_address = data.get('shippingAddress', {})
    shipping_state = shipping_address.get('state')
    tax = calculate_tax(total_amount, shipping_state)
    total_amount += tax
    
    # Get customer and shipping information
    shipping_address = data.get('shippingAddress', {})
    customer_email = data.get('customerEmail')
    customer_name = data.get('customerName')
    
    # Get Stripe customer ID if available
    stripe_customer_id = None
    if payment_intent.customer:
        stripe_customer_id = payment_intent.customer
    
    # Create order
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        currency='USD',
        status='Paid',  # Mark as paid since payment succeeded
        stripe_payment_intent_id=payment_intent_id,
        stripe_customer_id=stripe_customer_id,
        customer_email=customer_email,
        customer_name=customer_name,
        shipping_address_line1=shipping_address.get('line1'),
        shipping_address_line2=shipping_address.get('line2'),
        shipping_city=shipping_address.get('city'),
        shipping_state=shipping_address.get('state'),
        shipping_postal_code=shipping_address.get('postalCode'),
        shipping_country=shipping_address.get('country')
    )
    db.session.add(order)
    db.session.flush()
    
    # Create order items and reduce stock
    for item_data in order_items:
        order_item = OrderItem(
            order_id=order.id,
            book_id=item_data['book'].id,
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price']
        )
        db.session.add(order_item)
        
        # Reduce stock
        item_data['book'].stock_quantity -= item_data['quantity']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Order created and payment confirmed successfully',
        'order': order.to_dict(include_items=True)
    }), 201


@orders_bp.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """
    Stripe webhook endpoint to handle payment events.
    
    This endpoint receives events from Stripe about payment status changes.
    It can update order status based on payment events.
    
    Note: In production, you should verify the webhook signature using
    stripe.Webhook.construct_event() with your webhook signing secret.
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    stripe_secret_key = current_app.config.get('STRIPE_SECRET_KEY')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    
    if not stripe_secret_key:
        return jsonify({'error': 'Stripe not configured'}), 500
    
    stripe.api_key = stripe_secret_key
    
    try:
        # Verify webhook signature (if webhook secret is configured)
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            # In development, parse without verification
            import json
            event = json.loads(payload)
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            payment_intent_id = payment_intent['id']
            
            # Find order by payment intent ID
            order = Order.query.filter_by(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if order and order.status == 'Pending':
                order.status = 'Paid'
                db.session.commit()
                current_app.logger.info(f'Order {order.id} marked as Paid via webhook')
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            payment_intent_id = payment_intent['id']
            
            # Find order by payment intent ID
            order = Order.query.filter_by(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if order:
                # Optionally handle failed payments
                current_app.logger.warning(f'Payment failed for order {order.id}')
        
        return jsonify({'status': 'success'}), 200
        
    except ValueError as e:
        # Invalid payload
        current_app.logger.error(f'Invalid payload: {e}')
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        current_app.logger.error(f'Invalid signature: {e}')
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        current_app.logger.error(f'Webhook error: {e}')
        return jsonify({'error': str(e)}), 500

