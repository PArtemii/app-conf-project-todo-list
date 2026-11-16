from fastapi.testclient import TestClient

from main import app


def test_version():
    client = TestClient(app)
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()
    assert response.json()["version"] == "0.2.0"
    assert "team" in response.json()
    assert response.json()["team"] == "404"
