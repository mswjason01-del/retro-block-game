def test_public_pages(client):
    assert client.get('/').status_code == 200
    assert client.get('/leaderboard').status_code == 200
    assert client.get('/privacy').status_code == 200


def test_protected_pages_need_login(client):
    assert client.get('/game').status_code == 401
    assert client.get('/profile').status_code == 401
