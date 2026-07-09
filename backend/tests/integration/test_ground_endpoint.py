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


@requires_solr
def test_get_ground_prefix_filter_restricts_results(client):  # pragma: no cover
    response = client.get("/v3/api/ground", params={"text": "Marfan syndrome", "prefix": "MONDO"})
    assert response.status_code == 200
    results = response.json()
    assert results
    assert all(r["id"].startswith("MONDO:") for r in results)


@requires_solr
def test_get_ground_category_filter_restricts_results(client):  # pragma: no cover
    response = client.get("/v3/api/ground", params={"text": "Marfan syndrome", "category": "biolink:Disease"})
    assert response.status_code == 200
    results = response.json()
    assert results
    assert all(r["category"] == "biolink:Disease" for r in results)


@requires_solr
def test_post_ground_accepts_prefix_and_category_filters(client):  # pragma: no cover
    response = client.post(
        "/v3/api/ground",
        json={"content": "Marfan syndrome", "prefix": ["MONDO"], "category": ["biolink:Disease"]},
    )
    assert response.status_code == 200
    results = response.json()
    assert results
    assert all(r["id"].startswith("MONDO:") and r["category"] == "biolink:Disease" for r in results)


def test_get_ground_rejects_invalid_category(client):
    response = client.get("/v3/api/ground", params={"text": "Marfan syndrome", "category": "not-a-category"})
    assert response.status_code == 422


def test_post_ground_rejects_invalid_category(client):
    response = client.post(
        "/v3/api/ground",
        json={"content": "Marfan syndrome", "category": ["not-a-category"]},
    )
    assert response.status_code == 422
