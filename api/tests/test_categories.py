"""TC-09: Categories API tests."""


def test_tc09_categories(client, seed_data):
    """TC-09: List categories and get category by ID."""
    list_response = client.get('/api/categories')
    assert list_response.status_code == 200
    categories = list_response.get_json()['categories']
    assert len(categories) >= 2
    assert all('id' in cat and 'name' in cat for cat in categories)

    category_id = seed_data['fiction_category_id']
    detail_response = client.get(f'/api/categories/{category_id}')
    assert detail_response.status_code == 200
    category = detail_response.get_json()
    assert category['name'] == 'Fiction'
    assert category['id'] == category_id
