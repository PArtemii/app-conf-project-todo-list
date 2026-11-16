from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_version_answers():
    response = client.get("/version")
    assert response.status_code == 200
