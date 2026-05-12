"""Integration tests for the /ground API endpoint."""

import pytest
from fastapi.testclient import TestClient
from monarch_py.api.main import app
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

requires_solr = pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)


@pytest.fixture
def client():
    return TestClient(app)


@requires_solr
def test_get_ground_ranks_exact_synonym_first(client):  # pragma: no cover
    response = client.get("/v3/api/ground", params={"text": "kidney disease"})
    assert response.status_code == 200
    results = response.json()
    assert results
    assert results[0]["id"] == "MONDO:0005240"


@requires_solr
def test_post_ground_ranks_exact_synonym_first(client):  # pragma: no cover
    response = client.post("/v3/api/ground", json={"content": "kidney disease"})
    assert response.status_code == 200
    results = response.json()
    assert results
    assert results[0]["id"] == "MONDO:0005240"


@pytest.mark.parametrize("blank", ["", " ", "\t\n"])
def test_ground_returns_empty_for_blank_input(client, blank):
    response = client.get("/v3/api/ground", params={"text": blank})
    assert response.status_code == 200
    assert response.json() == []
