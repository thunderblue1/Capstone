"""TC-05 through TC-08, TC-19 through TC-21, TC-26: Books API tests."""
from models import Book, db


def test_tc05_list_books_with_pagination(client, seed_data):
    """TC-05: GET /api/books returns paginated JSON with valid book objects."""
    response = client.get('/api/books?page=1&per_page=10')

    assert response.status_code == 200
    data = response.get_json()
    assert 'books' in data
    assert 'total' in data
    assert 'pages' in data
    assert data['total'] >= 2
    assert len(data['books']) >= 2
    book = data['books'][0]
    assert 'title' in book
    assert 'author' in book
    assert 'price' in book


def test_tc06_search_books(client, seed_data):
    """TC-06: GET /api/books/search?q=fiction returns matching results."""
    response = client.get('/api/books/search?q=fiction')

    assert response.status_code == 200
    data = response.get_json()
    assert 'results' in data
    assert data['total'] >= 1
    assert any('fiction' in r.get('genre', '').lower() or 'fiction' in r.get('title', '').lower()
               for r in data['results'])


def test_tc07_book_detail_and_reviews(client, seed_data):
    """TC-07: Book detail and paginated reviews for existing book."""
    book_id = seed_data['fiction_book_id']

    detail = client.get(f'/api/books/{book_id}')
    assert detail.status_code == 200
    book = detail.get_json()
    assert book['title'] == 'The Fiction Trail'

    reviews = client.get(f'/api/books/{book_id}/reviews')
    assert reviews.status_code == 200
    review_data = reviews.get_json()
    assert 'reviews' in review_data
    assert 'pages' in review_data
    assert 'averageRating' in review_data


def test_tc08_featured_books(client, seed_data):
    """TC-08: GET /api/books/featured?limit=4 returns in-stock featured books."""
    response = client.get('/api/books/featured?limit=4')

    assert response.status_code == 200
    data = response.get_json()
    assert 'books' in data
    assert len(data['books']) <= 4
    for book in data['books']:
        assert book['stockQuantity'] > 0


def test_tc19_manager_create_book(client, manager_auth, seed_data):
    """TC-19: Manager POST /api/books creates book visible in GET."""
    payload = {
        'title': 'Manager Added Book',
        'author': 'Manager Author',
        'isbn13': '9784444444444',
        'price': 29.99,
        'stockQuantity': 50,
        'genre': 'Fiction',
        'categoryId': seed_data['fiction_category_id'],
    }
    response = client.post('/api/books/', json=payload, headers=manager_auth['headers'])

    assert response.status_code == 201
    created = response.get_json()['book']
    assert created['title'] == 'Manager Added Book'

    list_response = client.get('/api/books/')
    titles = [b['title'] for b in list_response.get_json()['books']]
    assert 'Manager Added Book' in titles


def test_tc20_manager_update_book(client, manager_auth, seed_data):
    """TC-20: Manager PUT /api/books/<id> updates fields."""
    book_id = seed_data['fiction_book_id']
    response = client.put(
        f'/api/books/{book_id}',
        json={'title': 'Updated Fiction Title'},
        headers=manager_auth['headers'],
    )

    assert response.status_code == 200
    assert response.get_json()['book']['title'] == 'Updated Fiction Title'


def test_tc21_manager_delete_book(client, manager_auth, seed_data, app):
    """TC-21: Manager DELETE /api/books/<id> removes book."""
    with app.app_context():
        book = Book(
            title='To Delete',
            author='Temp Author',
            isbn_13='9785555555555',
            price=9.99,
            stock_quantity=1,
        )
        db.session.add(book)
        db.session.commit()
        book_id = book.id

    delete_response = client.delete(f'/api/books/{book_id}', headers=manager_auth['headers'])
    assert delete_response.status_code == 200

    get_response = client.get(f'/api/books/{book_id}')
    assert get_response.status_code == 404


def test_tc26_customer_denied_book_post(client, customer_auth):
    """TC-26: Customer POST /api/books returns 403."""
    response = client.post(
        '/api/books/',
        json={
            'title': 'Forbidden',
            'author': 'Nobody',
            'isbn13': '9786666666666',
            'price': 9.99,
        },
        headers=customer_auth['headers'],
    )

    assert response.status_code == 403
