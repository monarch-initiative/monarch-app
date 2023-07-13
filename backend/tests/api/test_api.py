from fastapi.testclient import TestClient
from httpx import URL
from monarch_py.api.main import app

client = TestClient(app)


def test_root_redirects_to_docs():
    response = client.get("/")
    assert response.status_code == 200
    assert "/v3/docs" in URL(response.url).path


def test_api_redirects_to_docs():
    response = client.get("/api")
    assert response.status_code == 200
    assert "/v3/docs" in URL(response.url).path


def test_docs():
    response = client.get("/v3/docs")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"


def test_redoc():
    response = client.get("/v3/redoc")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
