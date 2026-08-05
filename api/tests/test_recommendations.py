"""TC-22 and TC-23: Recommendations API tests."""
from models import Book, Order, OrderItem, Review, User, db
from services.recommender import (
    CollaborativeFilteringRecommender,
    ContentBasedRecommender,
    RecommenderService,
)


def test_tc22_recommendations_for_you(client, customer_auth, seed_data):
    """TC-22: Personalized recommendations (GET /api/recommendations/personalized)."""
    response = client.get(
        '/api/recommendations/personalized',
        headers=customer_auth['headers'],
    )

    assert response.status_code == 200
    data = response.get_json()
    assert 'recommendations' in data
    assert isinstance(data['recommendations'], list)
    assert data['personalized'] is True


def test_tc23_similar_books(client, seed_data):
    """TC-23: GET /api/recommendations/similar/<book_id> returns similar list."""
    book_id = seed_data['fiction_book_id']
    response = client.get(f'/api/recommendations/similar/{book_id}')

    assert response.status_code == 200
    data = response.get_json()
    assert 'similar' in data
    assert isinstance(data['similar'], list)
    assert all(item['id'] != str(book_id) for item in data['similar'])
    assert data['algorithm'] == 'content_based'
    assert any(item['id'] == str(seed_data['fiction_book_2_id']) for item in data['similar'])


def test_content_based_personalized_uses_user_history(client, customer_auth, seed_data, app):
    """Sparse history stays on content-based (CF gated off)."""
    with app.app_context():
        review = Review(
            user_id=customer_auth['user']['id'],
            book_id=seed_data['fiction_book_id'],
            rating=5.0,
            comment='Loved this fiction adventure.',
        )
        db.session.add(review)
        db.session.commit()

    response = client.get(
        '/api/recommendations/personalized',
        headers=customer_auth['headers'],
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['algorithm'] == 'content_based'
    assert data['personalized'] is True
    assert data['basedOn']['cfEligible'] is False
    recommended_ids = [book['id'] for book in data['recommendations']]
    assert str(seed_data['fiction_book_id']) not in recommended_ids
    assert str(seed_data['fiction_book_2_id']) in recommended_ids


def test_search_based_content_recommendations(client, seed_data):
    """Search-based endpoint uses content model when recommender is enabled."""
    response = client.get('/api/recommendations/search-based?q=fiction%20adventure&limit=4')
    assert response.status_code == 200
    data = response.get_json()
    assert data['algorithm'] == 'content_based'
    assert len(data['recommendations']) >= 1


def test_content_based_recommender_unit():
    """Unit test for TF-IDF similar-book ranking."""
    model = ContentBasedRecommender()
    model.train({
        'books': [
            {
                'id': 1,
                'title': 'Forest Adventure',
                'author': 'A',
                'genre': 'Fiction',
                'category_name': 'Fiction',
                'description': 'A gripping fiction adventure in forests.',
                'popularity_score': 5,
            },
            {
                'id': 2,
                'title': 'Forest Quest',
                'author': 'A',
                'genre': 'Fiction',
                'category_name': 'Fiction',
                'description': 'Another fiction adventure through forests.',
                'popularity_score': 4,
            },
            {
                'id': 3,
                'title': 'Quantum Physics',
                'author': 'B',
                'genre': 'Science',
                'category_name': 'Non-Fiction',
                'description': 'Advanced physics textbook.',
                'popularity_score': 3,
            },
        ],
        'user_interactions': [
            {'user_id': 10, 'book_id': 1, 'weight': 5.0},
        ],
    })

    similar = model.get_similar_books(1, n=2)
    assert similar[0] == 2

    personalized = model.get_recommendations(10, n=2)
    assert 1 not in personalized
    assert 2 in personalized


def _dense_cf_payload():
    """Synthetic ratings dense enough for item–item CF."""
    # Users 1–2: fiction fans; 3–4: science fans; 5: fiction fan missing book 13
    ratings = [
        {'user_id': 1, 'book_id': 10, 'rating': 5.0},
        {'user_id': 1, 'book_id': 11, 'rating': 5.0},
        {'user_id': 1, 'book_id': 13, 'rating': 5.0},
        {'user_id': 1, 'book_id': 12, 'rating': 1.0},
        {'user_id': 2, 'book_id': 10, 'rating': 4.5},
        {'user_id': 2, 'book_id': 11, 'rating': 5.0},
        {'user_id': 2, 'book_id': 13, 'rating': 5.0},
        {'user_id': 2, 'book_id': 12, 'rating': 1.5},
        {'user_id': 3, 'book_id': 12, 'rating': 5.0},
        {'user_id': 3, 'book_id': 14, 'rating': 5.0},
        {'user_id': 3, 'book_id': 10, 'rating': 1.0},
        {'user_id': 4, 'book_id': 12, 'rating': 4.5},
        {'user_id': 4, 'book_id': 14, 'rating': 5.0},
        {'user_id': 4, 'book_id': 11, 'rating': 2.0},
        # Incomplete fiction profile — should surface book 13 via item–item
        {'user_id': 5, 'book_id': 10, 'rating': 5.0},
        {'user_id': 5, 'book_id': 11, 'rating': 4.5},
    ]
    purchases = [
        {'user_id': 2, 'book_id': 13, 'weight': 3.0},  # already rated; ignored for fill
    ]
    books = [
        {'id': 10, 'title': 'F1', 'author': 'A', 'genre': 'Fiction',
         'category_name': 'Fiction', 'description': 'fiction one', 'popularity_score': 5},
        {'id': 11, 'title': 'F2', 'author': 'A', 'genre': 'Fiction',
         'category_name': 'Fiction', 'description': 'fiction two', 'popularity_score': 4},
        {'id': 12, 'title': 'S1', 'author': 'B', 'genre': 'Science',
         'category_name': 'Science', 'description': 'science one', 'popularity_score': 3},
        {'id': 13, 'title': 'F3', 'author': 'A', 'genre': 'Fiction',
         'category_name': 'Fiction', 'description': 'fiction three', 'popularity_score': 4},
        {'id': 14, 'title': 'S2', 'author': 'B', 'genre': 'Science',
         'category_name': 'Science', 'description': 'science two', 'popularity_score': 2},
    ]
    return books, ratings, purchases


def test_collaborative_filtering_item_item_unit():
    """CF trains, gates cold users, and recommends from neighbors."""
    _books, ratings, purchases = _dense_cf_payload()
    model = CollaborativeFilteringRecommender()
    model.train({'ratings': ratings, 'user_interactions': purchases})

    assert model.is_ready
    assert model.method in {'item_item', 'svd'}
    assert model.can_recommend_for(5)
    assert not model.can_recommend_for(99)

    recs = model.get_recommendations(5, n=3)
    assert 10 not in recs and 11 not in recs
    assert 13 in recs


def test_collaborative_filtering_gates_sparse_matrix():
    """CF stays inactive when the matrix is too thin."""
    model = CollaborativeFilteringRecommender()
    model.train({
        'ratings': [
            {'user_id': 1, 'book_id': 1, 'rating': 5.0},
            {'user_id': 1, 'book_id': 2, 'rating': 4.0},
        ],
        'user_interactions': [],
    })
    assert not model.is_ready
    assert model.get_recommendations(1, n=5) == []


def test_hybrid_prefers_cf_when_eligible(tmp_path):
    """RecommenderService hybrid path reports collaborative when gated on."""
    books, ratings, purchases = _dense_cf_payload()
    interactions = [
        {'user_id': r['user_id'], 'book_id': r['book_id'], 'weight': r['rating']}
        for r in ratings
    ] + purchases

    service = RecommenderService(model_path=str(tmp_path / 'recommender'))
    service.initialize(force_retrain=True)
    service.train_all(books, ratings, interactions)

    assert service.cf_ready
    ids, label = service.recommend_for_user(user_id=5, n=3, algorithm='hybrid')
    assert label == 'collaborative'
    assert 13 in ids
    assert 10 not in ids and 11 not in ids
    assert (tmp_path / 'recommender' / 'cf.pkl').exists()


def test_personalized_collaborative_when_matrix_dense(
    client, customer_auth, seed_data, app
):
    """API personalized endpoint switches to collaborative with dense seed data."""
    with app.app_context():
        customer_id = customer_auth['user']['id']
        b1 = seed_data['fiction_book_id']
        b2 = seed_data['fiction_book_2_id']
        b3 = seed_data['science_book_id']

        # Extra in-stock book so CF has something unseen to recommend
        extra = Book(
            title='Mystery Forests Return',
            author='Alice Writer',
            isbn_13='9787777777777',
            price=16.0,
            stock_quantity=5,
            genre='Fiction',
            description='Another fiction adventure in forests.',
            category_id=seed_data['fiction_category_id'],
            popularity_score=5.0,
        )
        db.session.add(extra)
        db.session.flush()
        b4 = extra.id

        # Supporting users with overlapping tastes
        helpers = []
        for i in range(3):
            u = User(
                username=f'cf_helper_{i}',
                email=f'cf_helper_{i}@example.com',
            )
            u.set_password('StrongPass1!')
            db.session.add(u)
            db.session.flush()
            helpers.append(u.id)

        # Customer: two fiction likes (meets MIN_USER_INTERACTIONS)
        db.session.add_all([
            Review(user_id=customer_id, book_id=b1, rating=5.0, comment='great'),
            Review(user_id=customer_id, book_id=b2, rating=4.5, comment='also great'),
        ])

        # Helpers create matrix density + neighbor signal toward b4
        for uid in helpers:
            db.session.add_all([
                Review(user_id=uid, book_id=b1, rating=5.0, comment='x'),
                Review(user_id=uid, book_id=b2, rating=4.5, comment='x'),
                Review(user_id=uid, book_id=b4, rating=5.0, comment='x'),
                Review(user_id=uid, book_id=b3, rating=1.5, comment='x'),
            ])

        # Implicit purchase for one helper
        order = Order(user_id=helpers[0], total_amount=16.0, status='Paid')
        db.session.add(order)
        db.session.flush()
        db.session.add(
            OrderItem(order_id=order.id, book_id=b4, quantity=1, unit_price=16.0)
        )
        db.session.commit()

    response = client.get(
        '/api/recommendations/personalized',
        headers=customer_auth['headers'],
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['algorithm'] == 'collaborative'
    assert data['basedOn']['cfEligible'] is True
    recommended_ids = [book['id'] for book in data['recommendations']]
    assert str(b1) not in recommended_ids
    assert str(b2) not in recommended_ids
    assert str(b4) in recommended_ids
