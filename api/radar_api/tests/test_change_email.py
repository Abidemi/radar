import json

from radar_api.tests.fixtures import get_user
from radar.models.user_sessions import UserSession


def get_session_count(user):
    return UserSession.query.filter(UserSession.user == user, UserSession.is_active == True).count()  # noqa


def test_change_email(app):
    user = get_user('admin')

    client1 = app.test_client()
    client1.login(user)

    client2 = app.test_client()
    client2.login(user)

    # Check both clients are logged in
    assert client1.get('/patients').status_code == 200
    assert client2.get('/patients').status_code == 200

    assert get_session_count(user) == 2

    assert client1.post('/users/%s' % user.id, data={
        'current_password': 'password',
        'email': 'bar@example.org'
    }).status_code == 200

    assert get_session_count(user) == 1

    # Check second client is logged out
    assert client1.get('/patients').status_code == 200
    assert client2.get('/patients').status_code == 401

    client2.login(user)

    assert get_session_count(user) == 2

    assert client2.get('/patients').status_code == 200


def test_incorrect_password(app):
    user = get_user('admin')

    client1 = app.test_client()
    client1.login(user)

    client2 = app.test_client()
    client2.login(user)

    # Check both clients are logged in
    assert client1.get('/patients').status_code == 200
    assert client2.get('/patients').status_code == 200

    assert get_session_count(user) == 2

    response = client1.post('/users/%s' % user.id, data={
        'current_password': 'foobarbaz',
        'email': 'bar@example.org'
    })

    assert response.status_code == 422

    data = json.loads(response.data)

    assert data == {
        'errors': {
            'current_password': ['Incorrect password!']
        }
    }

    assert get_session_count(user) == 2

    # Check both clients are still logged in
    assert client1.get('/patients').status_code == 200
    assert client2.get('/patients').status_code == 200
