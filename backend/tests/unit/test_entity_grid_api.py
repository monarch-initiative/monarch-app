"""Unit tests for entity_grid API endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

from monarch_py.api.main import app
from monarch_py.api.entity_grid import _validate_entity_category, _get_grid, RowGrouping
from monarch_py.datamodels.category_enums import EntityCategory
from monarch_py.datamodels.model import EntityGridResponse
from monarch_py.implementations.solr.solr_implementation import SolrImplementation


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_grid_response():
    return EntityGridResponse(
        context_id="TEST:001",
        context_name="Test Entity",
        context_category="biolink:Disease",
        total_columns=0,
        total_rows=0,
        columns=[],
        rows=[],
        bins=[],
        cells={},
    )


# =====================================================================
# Tests for _validate_entity_category
# =====================================================================


def test_validate_entity_category_valid():
    mock_entity = MagicMock()
    mock_entity.category = "biolink:Disease"

    with patch.object(SolrImplementation, "get_entity", return_value=mock_entity):
        _validate_entity_category("MONDO:0007078", EntityCategory.DISEASE)


def test_validate_entity_category_list():
    mock_entity = MagicMock()
    mock_entity.category = ["biolink:Disease", "biolink:NamedThing"]

    with patch.object(SolrImplementation, "get_entity", return_value=mock_entity):
        _validate_entity_category("MONDO:0007078", EntityCategory.DISEASE)


def test_validate_entity_category_not_found():
    with patch.object(SolrImplementation, "get_entity", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            _validate_entity_category("MONDO:9999999", EntityCategory.DISEASE)
        assert exc_info.value.status_code == 404


def test_validate_entity_category_wrong_category():
    mock_entity = MagicMock()
    mock_entity.category = "biolink:Gene"

    with patch.object(SolrImplementation, "get_entity", return_value=mock_entity):
        with pytest.raises(HTTPException) as exc_info:
            _validate_entity_category("HGNC:4851", EntityCategory.DISEASE)
        assert exc_info.value.status_code == 400


def test_validate_entity_category_no_category():
    mock_entity = MagicMock()
    mock_entity.category = None

    with patch.object(SolrImplementation, "get_entity", return_value=mock_entity):
        with pytest.raises(HTTPException) as exc_info:
            _validate_entity_category("MONDO:0007078", EntityCategory.DISEASE)
        assert exc_info.value.status_code == 400


def test_validate_entity_category_exception():
    with patch.object(SolrImplementation, "get_entity", side_effect=Exception("Solr down")):
        with pytest.raises(HTTPException) as exc_info:
            _validate_entity_category("MONDO:0007078", EntityCategory.DISEASE)
        assert exc_info.value.status_code == 404


# =====================================================================
# Tests for _get_grid
# =====================================================================


def test_get_grid_returns_response(mock_grid_response):
    with patch.object(SolrImplementation, "get_entity_grid", return_value=mock_grid_response):
        result = _get_grid("MONDO:0007078", "case-phenotype", True, 1000)
        assert isinstance(result, EntityGridResponse)


def test_get_grid_raises_400_on_value_error():
    with patch.object(SolrImplementation, "get_entity_grid", side_effect=ValueError("exceeds limit")):
        with pytest.raises(HTTPException) as exc_info:
            _get_grid("MONDO:0007078", "case-phenotype", True, 1000)
        assert exc_info.value.status_code == 400


# =====================================================================
# Tests for get_traversable_associations endpoint
# =====================================================================


def test_traversable_associations_for_gene(client):
    response = client.get("/v3/api/entity-grid/traversable-associations/biolink:Gene")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for item in data:
        assert "category" in item
        assert "context_field" in item
        assert "target_category" in item


def test_traversable_associations_for_disease(client):
    response = client.get("/v3/api/entity-grid/traversable-associations/biolink:Disease")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_traversable_associations_unknown_category(client):
    response = client.get("/v3/api/entity-grid/traversable-associations/biolink:Unknown")
    assert response.status_code == 404


# =====================================================================
# Tests for RowGrouping enum
# =====================================================================


def test_row_grouping_histopheno():
    assert RowGrouping.HISTOPHENO.value == "histopheno"


def test_row_grouping_none():
    assert RowGrouping.NONE.value == "none"
