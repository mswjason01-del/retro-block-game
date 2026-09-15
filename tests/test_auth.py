from app.models import User
from app import db
from werkzeug.security import check_password_hash
from .conftest import csrf


def register(client, username="PlayerOne", password="password123"):
    client.get('/register')
    return client.post('/register', data={"csrf_token": csrf(client), "username": username, "password": password, "confirm_password": password}, follow_redirects=True)


def test_registration_hashes_password(app, client):
    response = register(client)
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username="PlayerOne").first()
        assert user and user.password_hash != "password123"
        assert check_password_hash(user.password_hash, "password123")


def test_duplicate_username_fails(client):
    register(client)
    client.post('/logout', data={"csrf_token": csrf(client)})
    response = register(client, "playerone")
    assert b"Username already exists" in response.data


def test_login_logout(client):
    register(client)
    client.post('/logout', data={"csrf_token": csrf(client)})
    client.get('/login')
    response = client.post('/login', data={"csrf_token": csrf(client), "username":"PlayerOne", "password":"password123"}, follow_redirects=True)
    assert b"Falling block game board" in response.data
    response = client.post('/logout', data={"csrf_token": csrf(client)}, follow_redirects=True)
    assert b"CREATE ACCOUNT" in response.data


def test_bad_login_fails(client):
    client.get('/login')
    response = client.post('/login', data={"csrf_token": csrf(client), "username":"nobody", "password":"incorrect"})
    assert b"Invalid username or password" in response.data
