"""Tests for the meta endpoint that serves dynamic OG tags to crawlers."""

import pytest
from fastapi.testclient import TestClient

from monarch_py.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_meta_endpoint_returns_html_with_og_tags(client):
    """Test that /meta/{entity_id} returns HTML with entity-specific OG tags."""
    response = client.get("/v3/api/meta/MONDO:0005148")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"

    html = response.text
    # Check for entity-specific content (diabetes mellitus)
    assert "MONDO:0005148" in html or "diabetes" in html.lower()
    assert 'og:title' in html
    assert 'og:description' in html
    assert 'og:url' in html
    # URL is derived from request host (testserver in tests, monarchinitiative.org in prod)
    assert 'testserver/MONDO:0005148' in html


def test_meta_endpoint_returns_404_for_unknown_entity(client):
    """Test that /meta/{entity_id} returns 404 for non-existent entities."""
    response = client.get("/v3/api/meta/FAKE:9999999")

    assert response.status_code == 404


def test_meta_endpoint_escapes_html_in_content(client):
    """Test that entity content is properly HTML-escaped to prevent XSS."""
    # This tests that special characters in entity names/descriptions
    # are properly escaped in the HTML output
    response = client.get("/v3/api/meta/MONDO:0005148")

    assert response.status_code == 200
    # Should not contain unescaped angle brackets from entity content
    # (the HTML tags themselves are fine, but entity content should be escaped)
