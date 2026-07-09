"""TC-22 and TC-23: Recommendations API tests."""


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
