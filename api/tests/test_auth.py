"""TC-01 through TC-04: Authentication tests."""
from tests.conftest import auth_headers, login_user, register_user


def test_tc01_register_new_user(client):
    """TC-01: Register new user — 201, user object, default role customer."""
    response = register_user(
        client,
        username='newuser',
        email='newuser@example.com',
        password='StrongPass1!',
    )

    assert response.status_code == 201
    data = response.get_json()
    assert 'user' in data
    assert data['user']['username'] == 'newuser'
    assert data['user']['email'] == 'newuser@example.com'
    assert data['user']['role'] == 'customer'
    assert 'accessToken' in data

    login_response = login_user(client, email='newuser@example.com', password='StrongPass1!')
    assert login_response.status_code == 200
    assert 'accessToken' in login_response.get_json()


def test_tc02_login_returns_jwt(client, customer_auth):
    """TC-02: Login returns JWT; GET /api/auth/me returns profile."""
    login_response = login_user(client)
    assert login_response.status_code == 200
    login_data = login_response.get_json()
    assert 'accessToken' in login_data

    me_response = client.get('/api/auth/me', headers=customer_auth['headers'])
    assert me_response.status_code == 200
    profile = me_response.get_json()
    assert profile['email'] == 'test@example.com'
    assert profile['username'] == 'testuser'


def test_tc03_update_profile(client, customer_auth):
    """TC-03: PUT /api/auth/me updates display fields."""
    response = client.put(
        '/api/auth/me',
        headers=customer_auth['headers'],
        json={'firstName': 'Updated', 'lastName': 'Name'},
    )
    assert response.status_code == 200
    assert response.get_json()['user']['firstName'] == 'Updated'

    me_response = client.get('/api/auth/me', headers=customer_auth['headers'])
    profile = me_response.get_json()
    assert profile['firstName'] == 'Updated'
    assert profile['lastName'] == 'Name'


def test_tc04_change_password(client, customer_auth):
    """TC-04: Change password — new login works with updated credentials."""
    old_token = customer_auth['access_token']

    change_response = client.post(
        '/api/auth/change-password',
        headers=customer_auth['headers'],
        json={'currentPassword': 'StrongPass1!', 'newPassword': 'NewStrong1!'},
    )
    assert change_response.status_code == 200

    # Existing token may still work until logout; new password must work for login.
    new_login = login_user(client, password='NewStrong1!')
    assert new_login.status_code == 200
    assert 'accessToken' in new_login.get_json()

    # Old password should fail
    old_login = login_user(client, password='StrongPass1!')
    assert old_login.status_code == 401

    # Old token still valid until explicitly revoked (documented behavior)
    me_with_old = client.get('/api/auth/me', headers=auth_headers(old_token))
    assert me_with_old.status_code == 200
