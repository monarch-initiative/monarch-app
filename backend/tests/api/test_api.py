from fastapi.testclient import TestClient
from httpx import URL
from unittest.mock import patch
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


def test_releases():
    response = client.get("/v3/api/releases?limit=2")
    assert response.status_code == 200
    releases = [release["version"] for release in response.json()]
    assert [i in ["latest", "previous"] for i in releases]


def test_release_metadata():
    response = client.get("/v3/api/releases?release=latest")
    assert response.status_code == 200
    assert response.json()["version"] == "latest"
    assert response.json()["url"] == "https://data.monarchinitiative.org/monarch-kg/latest/index.html"


@patch.dict(
    "os.environ",
    {"MONARCH_KG_VERSION": "2025-06-05", "KG_DEPLOYMENT_DATE": "2025-06-12T16:08:26Z", "MONARCH_API_VERSION": "1.17.0"},
)
def test_current_deployment_info():
    """Test the /v3/api/releases/current endpoint with mocked environment variables."""
    response = client.get("/v3/api/releases/current")
    assert response.status_code == 200

    data = response.json()
    assert data["kg_version"] == "2025-06-05"
    assert data["deployment_date"] == "2025-06-12T16:08:26Z"
    assert data["api_version"] == "1.17.0"
    assert data["release_date"] == "2025-06-05"


@patch.dict("os.environ", {}, clear=True)
def test_current_deployment_info_no_env_vars():
    """Test the /v3/api/releases/current endpoint with no environment variables."""
    response = client.get("/v3/api/releases/current")
    assert response.status_code == 200

    data = response.json()
    assert data["kg_version"] is None
    assert data["deployment_date"] is None
    assert data["api_version"] is None
    assert data["release_date"] is None
