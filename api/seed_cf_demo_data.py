"""
Seed synthetic users, ratings, and purchases for collaborative filtering demos.

The in-repo catalog is often too sparse for a usable CF matrix. This script
adds demo personas and interactions without changing schema.

Usage (from the api/ directory):
    python seed_cf_demo_data.py

Optional:
    CF_SEED_PASSWORD=YourPass1!   # password for demo users (default DemoPass1!)
    CF_SEED_FORCE=1               # clear prior cf_demo_* reviews/orders and reseed
"""
from __future__ import annotations

import os
import sys
from decimal import Decimal

from App import create_app
from models import Book, Order, OrderItem, Review, User, db

DEMO_PASSWORD = os.environ.get('CF_SEED_PASSWORD', 'DemoPass1!')
DEMO_USER_PREFIX = 'cf_demo_user_'
DEMO_EMAIL_DOMAIN = 'cf-demo.curiousbooks.local'

# Persona preference clusters: list of (genre_keyword_substring, rating) patterns
# applied against book.genre / title. Falls back to round-robin ratings.
PERSONAS = [
    {
        'username': f'{DEMO_USER_PREFIX}01',
        'email': f'user01@{DEMO_EMAIL_DOMAIN}',
        'first_name': 'Casey',
        'last_name': 'FictionFan',
        'liked_genres': {'Fiction', 'Mystery', 'Fantasy'},
        'liked_rating': 5.0,
        'other_rating': 2.0,
    },
    {
        'username': f'{DEMO_USER_PREFIX}02',
        'email': f'user02@{DEMO_EMAIL_DOMAIN}',
        'first_name': 'Jordan',
        'last_name': 'StoryLover',
        'liked_genres': {'Fiction', 'Mystery', 'Fantasy'},
        'liked_rating': 4.5,
        'other_rating': 2.5,
    },
    {
        'username': f'{DEMO_USER_PREFIX}03',
        'email': f'user03@{DEMO_EMAIL_DOMAIN}',
        'first_name': 'Riley',
        'last_name': 'NovelReader',
        'liked_genres': {'Fiction', 'Mystery', 'Fantasy'},
        'liked_rating': 4.0,
        'other_rating': 1.5,
    },
    {
        'username': f'{DEMO_USER_PREFIX}04',
        'email': f'user04@{DEMO_EMAIL_DOMAIN}',
        'first_name': 'Avery',
        'last_name': 'ScienceBuff',
        'liked_genres': {'Science', 'Non-Fiction', 'History', 'Biography'},
        'liked_rating': 5.0,
        'other_rating': 2.0,
    },
    {
        'username': f'{DEMO_USER_PREFIX}05',
        'email': f'user05@{DEMO_EMAIL_DOMAIN}',
        'first_name': 'Morgan',
        'last_name': 'FactFinder',
        'liked_genres': {'Science', 'Non-Fiction', 'History', 'Biography'},
        'liked_rating': 4.5,
        'other_rating': 2.0,
    },
    {
        'username': f'{DEMO_USER_PREFIX}06',
        'email': f'user06@{DEMO_EMAIL_DOMAIN}',
        'first_name': 'Quinn',
        'last_name': 'MixedTaste',
        'liked_genres': {'Fiction', 'Science'},
        'liked_rating': 4.0,
        'other_rating': 3.0,
    },
]


def _genre_matches(book: Book, liked_genres: set) -> bool:
    genre = (book.genre or '').strip()
    if genre in liked_genres:
        return True
    # Loose match on substring for sparse catalogs
    lower = genre.lower()
    return any(g.lower() in lower or lower in g.lower() for g in liked_genres if g)


def _ensure_users():
    users = []
    for persona in PERSONAS:
        user = User.query.filter_by(email=persona['email']).first()
        if user is None:
            user = User(
                username=persona['username'],
                email=persona['email'],
                first_name=persona['first_name'],
                last_name=persona['last_name'],
            )
            user.set_password(DEMO_PASSWORD)
            db.session.add(user)
            db.session.flush()
            print(f'  Created user {user.username}')
        else:
            print(f'  Using existing user {user.username}')
        users.append((user, persona))
    db.session.commit()
    return users


def _clear_demo_interactions(users):
    user_ids = [u.id for u, _ in users]
    reviews = Review.query.filter(Review.user_id.in_(user_ids)).all()
    for review in reviews:
        db.session.delete(review)

    orders = Order.query.filter(Order.user_id.in_(user_ids)).all()
    for order in orders:
        db.session.delete(order)
    db.session.commit()
    print(f'  Cleared prior demo reviews/orders for {len(user_ids)} users')


def _seed_ratings_and_orders(users, books):
    if len(books) < 3:
        print('Need at least 3 books in the catalog to seed CF data.')
        return 0, 0

    ratings_added = 0
    orders_added = 0

    for user, persona in users:
        liked = []
        other = []
        for book in books:
            if _genre_matches(book, persona['liked_genres']):
                liked.append(book)
            else:
                other.append(book)

        # Ensure each persona rates enough titles for CF gating
        to_rate = []
        for book in liked[:4]:
            to_rate.append((book, persona['liked_rating']))
        for book in other[:2]:
            to_rate.append((book, persona['other_rating']))

        # If genres don't separate well, rate a spread of books
        if len(to_rate) < 3:
            to_rate = []
            for idx, book in enumerate(books[:5]):
                rating = persona['liked_rating'] if idx % 2 == 0 else persona['other_rating']
                to_rate.append((book, rating))

        for book, rating in to_rate:
            existing = Review.query.filter_by(user_id=user.id, book_id=book.id).first()
            if existing:
                continue
            db.session.add(
                Review(
                    user_id=user.id,
                    book_id=book.id,
                    rating=float(rating),
                    comment=f'Demo CF seed rating ({persona["username"]})',
                )
            )
            ratings_added += 1

            # Refresh simple aggregates used by catalog UI
            book.review_count = (book.review_count or 0) + 1
            if book.average_rating:
                book.average_rating = (
                    (float(book.average_rating) * (book.review_count - 1)) + float(rating)
                ) / book.review_count
            else:
                book.average_rating = float(rating)

        # One paid order on a liked (or first) book for implicit signal
        purchase_book = liked[0] if liked else books[0]
        order = Order(
            user_id=user.id,
            total_amount=Decimal(str(purchase_book.price or 19.99)),
            status='Paid',
            customer_email=user.email,
            customer_name=f'{user.first_name} {user.last_name}',
        )
        db.session.add(order)
        db.session.flush()
        db.session.add(
            OrderItem(
                order_id=order.id,
                book_id=purchase_book.id,
                quantity=1,
                unit_price=purchase_book.price or Decimal('19.99'),
            )
        )
        orders_added += 1

    db.session.commit()
    return ratings_added, orders_added


def main():
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    force = os.environ.get('CF_SEED_FORCE', '').lower() in {'1', 'true', 'yes'}

    with app.app_context():
        books = Book.query.order_by(Book.id).all()
        print(f'Catalog books: {len(books)}')
        if len(books) < 3:
            print('Aborting: add more books before seeding CF demo data.')
            return 1

        print('Ensuring demo users...')
        users = _ensure_users()

        if force:
            _clear_demo_interactions(users)

        print('Seeding ratings and purchases...')
        ratings_added, orders_added = _seed_ratings_and_orders(users, books)
        print(f'Added {ratings_added} reviews and {orders_added} paid orders.')
        print(
            f'Demo login password for {DEMO_USER_PREFIX}* users: {DEMO_PASSWORD}'
        )
        print('Next: python train_recommender.py')
        return 0


if __name__ == '__main__':
    sys.exit(main())
