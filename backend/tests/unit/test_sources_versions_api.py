"""Unit tests for the /sources/versions FastAPI route.

Covers HTTP/caching behavior in `monarch_py.api.sources_versions`. The
underlying resolution logic is exercised in `test_source_versions.py`.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi.testclient import TestClient

from monarch_py.api import sources_versions as route
from monarch_py.api.main import app

VALID_RECEIPT_YAML = """\
id: monarch-kg
version: 2026-05-07
generated_at: "2026-05-07T16:11:30Z"
sources:
  - id: hgnc-ingest
    version: 2026-05-01
    sources:
      - id: infores:hgnc
        name: HUGO Gene Nomenclature Committee
        version: 2026-05-01
        version_method: http_last_modified
"""


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache():
    """Reset the module-level receipt cache between tests."""
    route._cache.clear()
    yield
    route._cache.clear()


def _ok_response(text: str = VALID_RECEIPT_YAML):
    resp = MagicMock()
    resp.text = text
    resp.raise_for_status = MagicMock()
    return resp


def test_endpoint_returns_serialized_receipt(client):
    with patch("monarch_py.api.sources_versions.requests.get", return_value=_ok_response()) as g:
        r = client.get("/v3/api/sources/versions")
    assert r.status_code == 200
    body = r.json()
    assert body["release"] == "2026-05-07"
    assert body["generated_at"] == "2026-05-07T16:11:30Z"
    assert body["by_producer"]["hgnc-ingest"]["infores:hgnc"]["version"] == "2026-05-01"
    assert body["canonical_producer"]["infores:hgnc"] == "hgnc-ingest"
    # Dropped from the response — confirm they don't leak back in.
    assert "disagreements" not in body
    assert "version_drift" not in body
    g.assert_called_once()
    assert "monarch-kg/latest/metadata.yaml" in g.call_args.args[0]


def test_endpoint_caches_within_ttl(client):
    with patch("monarch_py.api.sources_versions.requests.get", return_value=_ok_response()) as g:
        client.get("/v3/api/sources/versions")
        client.get("/v3/api/sources/versions")
    # Second call should be served from the in-memory cache.
    assert g.call_count == 1


def test_endpoint_refetches_when_ttl_expired(client):
    # Seed the cache with an entry older than the TTL by patching time.
    with patch("monarch_py.api.sources_versions.requests.get", return_value=_ok_response()) as g:
        with patch("monarch_py.api.sources_versions.time.time", return_value=0.0):
            client.get("/v3/api/sources/versions")
        # Jump past the TTL window.
        with patch(
            "monarch_py.api.sources_versions.time.time",
            return_value=route._CACHE_TTL_SECONDS + 1,
        ):
            client.get("/v3/api/sources/versions")
    assert g.call_count == 2


def test_dev_flag_hits_dev_mirror(client):
    with patch("monarch_py.api.sources_versions.requests.get", return_value=_ok_response()) as g:
        r = client.get("/v3/api/sources/versions", params={"dev": "true"})
    assert r.status_code == 200
    assert "monarch-kg-dev/latest/metadata.yaml" in g.call_args.args[0]


def test_dev_flag_caches_separately_from_prod(client):
    """Dev and prod responses share the same `release` but are keyed
    independently — flipping the flag should trigger a refetch."""
    with patch("monarch_py.api.sources_versions.requests.get", return_value=_ok_response()) as g:
        client.get("/v3/api/sources/versions")
        client.get("/v3/api/sources/versions", params={"dev": "true"})
    assert g.call_count == 2


def test_network_error_returns_502(client):
    err = requests.ConnectionError("network down")
    with patch("monarch_py.api.sources_versions.requests.get", side_effect=err):
        r = client.get("/v3/api/sources/versions")
    assert r.status_code == 502
    assert "Failed to fetch build receipt" in r.json()["detail"]


def test_http_error_returns_502(client):
    resp = MagicMock()
    resp.raise_for_status = MagicMock(side_effect=requests.HTTPError("404 Not Found"))
    with patch("monarch_py.api.sources_versions.requests.get", return_value=resp):
        r = client.get("/v3/api/sources/versions", params={"release": "1900-01-01"})
    assert r.status_code == 502


def test_invalid_yaml_returns_502(client):
    with patch(
        "monarch_py.api.sources_versions.requests.get",
        return_value=_ok_response(text="this: is: not: valid: yaml: : :"),
    ):
        r = client.get("/v3/api/sources/versions")
    assert r.status_code == 502
    assert "not valid YAML" in r.json()["detail"]


def test_legacy_shape_without_top_level_id_returns_502(client):
    """Pre-collapse receipts lacked a top-level `id`; the route should reject
    them with a 502 pointing the caller at `?dev=true`."""
    legacy = "sources:\n  - id: hgnc-ingest\n    version: 2026-05-01\n"
    with patch(
        "monarch_py.api.sources_versions.requests.get",
        return_value=_ok_response(text=legacy),
    ):
        r = client.get("/v3/api/sources/versions")
    assert r.status_code == 502
    assert "dev=true" in r.json()["detail"]


def test_release_with_path_traversal_returns_400(client):
    """The `release` query param is interpolated into the upstream URL —
    reject anything that could break out of the expected path segment."""
    with patch("monarch_py.api.sources_versions.requests.get") as g:
        r = client.get(
            "/v3/api/sources/versions",
            params={"release": "../latest"},
        )
    assert r.status_code == 400
    g.assert_not_called()


def test_settings_default_drives_dev_when_flag_unset(client):
    """When the client passes no `dev` query param, the route falls back to
    the `MONARCH_KG_USE_DEV` env-var-derived setting."""
    with patch("monarch_py.api.sources_versions.requests.get", return_value=_ok_response()) as g:
        with patch.object(route.settings, "monarch_kg_use_dev", True):
            client.get("/v3/api/sources/versions")
    assert "monarch-kg-dev/" in g.call_args.args[0]
