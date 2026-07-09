"""TC-16 through TC-18: Reviews API tests."""


def test_tc16_create_review(client, customer_auth, seed_data):
    """TC-16: POST /api/reviews creates review with JWT."""
    book_id = seed_data['fiction_book_id']
    response = client.post(
        '/api/reviews/',
        headers=customer_auth['headers'],
        json={'bookId': book_id, 'rating': 4, 'comment': 'Great read!'},
    )

    assert response.status_code == 201
    review = response.get_json()['review']
    assert review['rating'] == 4
    assert review['text'] == 'Great read!'


def test_tc17_edit_delete_own_review(client, customer_auth, second_customer_auth, seed_data):
    """TC-17: Owner can PUT/DELETE review; other user gets 403."""
    book_id = seed_data['fiction_book_id']
    create_response = client.post(
        '/api/reviews/',
        headers=customer_auth['headers'],
        json={'bookId': book_id, 'rating': 3, 'text': 'Okay book'},
    )
    review_id = create_response.get_json()['review']['id']

    update_response = client.put(
        f'/api/reviews/{review_id}',
        headers=customer_auth['headers'],
        json={'rating': 5, 'text': 'Actually loved it'},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()['review']['rating'] == 5

    forbidden = client.put(
        f'/api/reviews/{review_id}',
        headers=second_customer_auth['headers'],
        json={'rating': 1},
    )
    assert forbidden.status_code == 403

    delete_response = client.delete(f'/api/reviews/{review_id}', headers=customer_auth['headers'])
    assert delete_response.status_code == 200


def test_tc18_reviews_by_book(client, customer_auth, seed_data):
    """TC-18: GET /api/reviews/book/<id> lists reviews with aggregates."""
    book_id = seed_data['fiction_book_id']
    client.post(
        '/api/reviews/',
        headers=customer_auth['headers'],
        json={'bookId': book_id, 'rating': 4, 'comment': 'Enjoyed it'},
    )

    response = client.get(f'/api/reviews/book/{book_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['total'] >= 1
    assert 'averageRating' in data
    assert 'reviewCount' in data
    assert len(data['reviews']) >= 1
