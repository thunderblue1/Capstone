"""Shared fixtures for Curious Books API tests (TC-01 through TC-28)."""
import os
import shutil

os.environ.setdefault('FLASK_ENV', 'testing')

import pytest

from App import create_app
from constants.roles import MANAGER
from limiter import limiter
from models import Book, Category, Order, OrderItem, User, db
from services.recommender import reset_recommender_service


@pytest.fixture
def app():
    """Flask app with in-memory SQLite and rate limiting disabled."""
    reset_recommender_service()
    application = create_app('testing')
    limiter.enabled = False
    model_path = application.config.get('RECOMMENDER_MODEL_PATH')
    if model_path and os.path.isdir(model_path):
        shutil.rmtree(model_path, ignore_errors=True)
    yield application
    reset_recommender_service()
    if model_path and os.path.isdir(model_path):
        shutil.rmtree(model_path, ignore_errors=True)


@pytest.fixture
def client(app):
    """HTTP test client with fresh database per test."""
    with app.app_context():
        db.drop_all()
        db.create_all()
    reset_recommender_service()
    return app.test_client()


@pytest.fixture
def api_key_client(app):
    """Client when API key middleware is enabled (TC-25)."""
    application = create_app('testing_with_api_key')
    limiter.enabled = False
    with application.app_context():
        db.drop_all()
        db.create_all()
    return application.test_client()


@pytest.fixture
def api_key_headers():
    return {'X-API-Key': 'test-api-key'}


@pytest.fixture
def seed_data(app):
    """Categories and books for catalog/order tests."""
    with app.app_context():
        fiction = Category(name='Fiction')
        nonfiction = Category(name='Non-Fiction')
        db.session.add_all([fiction, nonfiction])
        db.session.flush()

        books = [
            Book(
                title='The Fiction Trail',
                author='Alice Writer',
                isbn_13='9781111111111',
                price=19.99,
                stock_quantity=10,
                genre='Fiction',
                description='A gripping fiction adventure through mysterious forests.',
                category_id=fiction.id,
                popularity_score=8.0,
                average_rating=4.5,
            ),
            Book(
                title='Science Explained',
                author='Bob Scholar',
                isbn_13='9782222222222',
                price=24.99,
                stock_quantity=5,
                genre='Science',
                description='Non-fiction science primer covering physics and biology.',
                category_id=nonfiction.id,
                popularity_score=6.0,
                average_rating=4.0,
            ),
            Book(
                title='Out of Stock Tale',
                author='Carol Author',
                isbn_13='9783333333333',
                price=14.99,
                stock_quantity=0,
                genre='Fiction',
                description='A fiction story that is currently unavailable.',
                category_id=fiction.id,
                popularity_score=1.0,
            ),
            Book(
                title='Another Fiction Journey',
                author='Alice Writer',
                isbn_13='9786666666666',
                price=18.50,
                stock_quantity=7,
                genre='Fiction',
                description='A gripping fiction adventure with heroes and forests.',
                category_id=fiction.id,
                popularity_score=7.0,
                average_rating=4.2,
            ),
        ]
        db.session.add_all(books)
        db.session.commit()

        return {
            'fiction_category_id': fiction.id,
            'nonfiction_category_id': nonfiction.id,
            'fiction_book_id': books[0].id,
            'science_book_id': books[1].id,
            'out_of_stock_book_id': books[2].id,
            'fiction_book_2_id': books[3].id,
        }


def register_user(client, username='testuser', email='test@example.com', password='StrongPass1!'):
    """Register via API and return response JSON."""
    response = client.post(
        '/api/auth/register',
        json={'username': username, 'email': email, 'password': password},
    )
    return response


def login_user(client, email='test@example.com', password='StrongPass1!'):
    """Login via API and return response JSON."""
    response = client.post(
        '/api/auth/login',
        json={'email': email, 'password': password},
    )
    return response


def auth_headers(access_token, extra=None):
    """Build Authorization header for JWT-protected routes."""
    headers = {'Authorization': f'Bearer {access_token}'}
    if extra:
        headers.update(extra)
    return headers


@pytest.fixture
def customer_auth(client):
    """Registered customer with JWT access token."""
    response = register_user(client)
    data = response.get_json()
    return {
        'user': data['user'],
        'access_token': data['accessToken'],
        'refresh_token': data['refreshToken'],
        'headers': auth_headers(data['accessToken']),
    }


@pytest.fixture
def manager_auth(client, app):
    """Registered user promoted to manager role."""
    response = register_user(client, username='manager1', email='manager@example.com')
    data = response.get_json()
    with app.app_context():
        user = User.query.get(data['user']['id'])
        user.role = MANAGER
        db.session.commit()
    return {
        'user': data['user'],
        'access_token': data['accessToken'],
        'headers': auth_headers(data['accessToken']),
    }


@pytest.fixture
def second_customer_auth(client):
    """Second customer for cross-user authorization tests."""
    response = register_user(client, username='user2', email='user2@example.com', password='OtherPass1!')
    data = response.get_json()
    return {
        'user': data['user'],
        'access_token': data['accessToken'],
        'headers': auth_headers(data['accessToken']),
    }


def create_order_for_user(app, user_id, book_id, quantity=1, status='Pending', unit_price=19.99):
    """Insert an order directly for isolation tests."""
    with app.app_context():
        order = Order(user_id=user_id, total_amount=unit_price * quantity, status=status)
        db.session.add(order)
        db.session.flush()
        db.session.add(
            OrderItem(
                order_id=order.id,
                book_id=book_id,
                quantity=quantity,
                unit_price=unit_price,
            )
        )
        db.session.commit()
        return order.id
