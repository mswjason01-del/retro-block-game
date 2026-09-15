from .test_auth import register
from .conftest import csrf


def game_start(client):
    return client.post('/api/game/start', headers={"X-CSRF-Token": csrf(client)}).get_json()['session_id']


def finish(client, session_id, score, lines, level):
    return client.post('/api/game/finish', headers={"X-CSRF-Token": csrf(client)}, json={"session_id":session_id,"score":score,"lines":lines,"level":level})


def test_score_save_and_high_score(client):
    register(client)
    first = finish(client, game_start(client), 800, 4, 1).get_json()
    assert first['new_high_score'] and first['high_score'] == 800
    second = finish(client, game_start(client), 300, 2, 1).get_json()
    assert not second['new_high_score'] and second['high_score'] == 800


def test_leaderboard_sorts(client):
    register(client, 'Alpha')
    finish(client, game_start(client), 1000, 4, 1)
    client.post('/logout', data={"csrf_token": csrf(client)})
    register(client, 'Bravo')
    finish(client, game_start(client), 1600, 4, 1)
    players = client.get('/api/leaderboard').get_json()['players']
    assert [p['username'] for p in players[:2]] == ['Bravo', 'Alpha']


def test_invalid_or_unauthorized_result_rejected(client):
    assert client.post('/api/game/start').status_code == 401
    register(client)
    response = finish(client, game_start(client), 99999999, 0, 1)
    assert response.status_code == 400
