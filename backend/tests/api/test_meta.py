"""Tests for the meta endpoint that serves dynamic OG tags to crawlers."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from monarch_py.api.main import app
from monarch_py.datamodels.model import Node


@pytest.fixture
def client():
    return TestClient(app)


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_entity")
def test_meta_endpoint_returns_html_with_og_tags(mock_get_entity, client, node):
    """Test that /meta/{entity_id} returns HTML with entity-specific OG tags."""
    mock_get_entity.return_value = Node(**node)
    response = client.get("/v3/api/meta/MONDO:0020121")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"

    html = response.text
    assert "MONDO:0020121" in html or "muscular dystrophy" in html.lower()
    assert 'og:title' in html
    assert 'og:description' in html
    assert 'og:url' in html
    assert 'testserver/MONDO:0020121' in html


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_entity")
def test_meta_endpoint_returns_404_for_unknown_entity(mock_get_entity, client):
    """Test that /meta/{entity_id} returns 404 for non-existent entities."""
    mock_get_entity.return_value = None
    response = client.get("/v3/api/meta/FAKE:9999999")

    assert response.status_code == 404


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_entity")
def test_meta_endpoint_escapes_html_in_content(mock_get_entity, client):
    """Test that entity content is properly HTML-escaped to prevent XSS."""
    mock_get_entity.return_value = Node(
        id="TEST:001",
        category="biolink:Disease",
        name='<script>alert("xss")</script>',
        description='A "test" <b>entity</b> with & special chars',
        provided_by="test",
        association_counts=[],
    )
    response = client.get("/v3/api/meta/TEST:001")

    assert response.status_code == 200
    html = response.text
    # Jinja2 autoescape should escape angle brackets
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
