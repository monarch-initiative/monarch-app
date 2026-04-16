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
# Tests for child-disease-phenotype-grid endpoint
# =====================================================================


def test_child_disease_phenotype_grid_endpoint(client, mock_grid_response):
    """Child disease-phenotype grid endpoint should validate and call _get_grid."""
    mock_entity = MagicMock()
    mock_entity.category = "biolink:Disease"

    with patch.object(SolrImplementation, "get_entity", return_value=mock_entity):
        with patch.object(SolrImplementation, "get_entity_grid", return_value=mock_grid_response):
            response = client.get("/v3/api/entity-grid/MONDO:0021060/child-disease-phenotype-grid")
            assert response.status_code == 200
            data = response.json()
            assert data["context_id"] == "TEST:001"


def test_child_disease_phenotype_grid_rejects_gene(client):
    """Child disease-phenotype grid should reject non-disease entities."""
    mock_entity = MagicMock()
    mock_entity.category = "biolink:Gene"

    with patch.object(SolrImplementation, "get_entity", return_value=mock_entity):
        response = client.get("/v3/api/entity-grid/HGNC:4851/child-disease-phenotype-grid")
        assert response.status_code == 400


def test_child_disease_phenotype_grid_default_limit(client, mock_grid_response):
    """Default limit should be 100 for child-disease-phenotype grid."""
    mock_entity = MagicMock()
    mock_entity.category = "biolink:Disease"

    with patch.object(SolrImplementation, "get_entity", return_value=mock_entity):
        with patch.object(SolrImplementation, "get_entity_grid", return_value=mock_grid_response) as mock_get_grid:
            client.get("/v3/api/entity-grid/MONDO:0021060/child-disease-phenotype-grid")
            call_kwargs = mock_get_grid.call_args.kwargs
            assert call_kwargs["limit"] == 100
            assert call_kwargs["grid_type"] == "child-disease-phenotype"


# =====================================================================
# Tests for generic endpoint with column_predicate
# =====================================================================


def test_generic_grid_with_column_predicate(client, mock_grid_response):
    """Generic endpoint should accept column_predicate parameter."""
    with patch.object(SolrImplementation, "get_generic_entity_grid", return_value=mock_grid_response) as mock_get_grid:
        response = client.get(
            "/v3/api/entity-grid/MONDO:0021060",
            params={
                "column_association_category": "biolink:Association",
                "row_association_category": "biolink:DiseaseToPhenotypicFeatureAssociation",
                "column_predicate": "biolink:subclass_of",
            },
        )
        assert response.status_code == 200
        call_kwargs = mock_get_grid.call_args.kwargs
        assert call_kwargs["column_predicates"] == ["biolink:subclass_of"]


def test_generic_grid_without_column_predicate(client, mock_grid_response):
    """Generic endpoint should work without column_predicate (defaults to None)."""
    with patch.object(SolrImplementation, "get_generic_entity_grid", return_value=mock_grid_response) as mock_get_grid:
        response = client.get(
            "/v3/api/entity-grid/MONDO:0021060",
            params={
                "column_association_category": "biolink:Association",
                "row_association_category": "biolink:DiseaseToPhenotypicFeatureAssociation",
            },
        )
        assert response.status_code == 200
        call_kwargs = mock_get_grid.call_args.kwargs
        assert call_kwargs["column_predicates"] is None


def test_generic_grid_with_multiple_column_predicates(client, mock_grid_response):
    """Generic endpoint should accept multiple column_predicate values."""
    with patch.object(SolrImplementation, "get_generic_entity_grid", return_value=mock_grid_response) as mock_get_grid:
        response = client.get(
            "/v3/api/entity-grid/MONDO:0021060",
            params={
                "column_association_category": "biolink:Association",
                "row_association_category": "biolink:DiseaseToPhenotypicFeatureAssociation",
                "column_predicate": [
                    "biolink:subclass_of",
                    "biolink:has_phenotype",
                ],
            },
        )
        assert response.status_code == 200
        call_kwargs = mock_get_grid.call_args.kwargs
        assert len(call_kwargs["column_predicates"]) == 2


# =====================================================================
# Tests for RowGrouping enum
# =====================================================================


def test_row_grouping_histopheno():
    assert RowGrouping.HISTOPHENO.value == "histopheno"


def test_row_grouping_none():
    assert RowGrouping.NONE.value == "none"
