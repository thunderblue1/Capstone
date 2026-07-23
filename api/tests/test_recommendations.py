"""TC-22 and TC-23: Recommendations API tests."""
from models import Review, db
from services.recommender import ContentBasedRecommender


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
    """Personalized content-based path ranks similar books after a review."""
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
