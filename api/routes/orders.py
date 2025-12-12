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
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc
from models import db, Order, OrderItem, Book

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

