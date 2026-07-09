"""TC-24 and TC-25: Health check and API key security tests."""


def test_tc24_health_check(client):
    """TC-24: GET /api/health returns healthy status."""
    response = client.get('/api/health')

    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'CuriousBooks API'


def test_tc25_api_key_required_when_configured(api_key_client, api_key_headers, seed_data):
    """TC-25: Missing API key returns 403; valid key allows access."""
    without_key = api_key_client.get('/api/books/')
    assert without_key.status_code == 403
    assert 'API key' in without_key.get_json()['error']

    with_key = api_key_client.get('/api/books/', headers=api_key_headers)
    assert with_key.status_code == 200

    # Health endpoint remains public
    health = api_key_client.get('/api/health')
    assert health.status_code == 200
