from main import app
from fastapi.testclient import TestClient

def test_get_version():
    client = TestClient(app)
    response = client.get('/version')
    assert 'version' in response.json()
    assert 'team' in response.json()
    assert response.json()['version'] == '0.2.0'
    assert response.json()['team'] == '404'
