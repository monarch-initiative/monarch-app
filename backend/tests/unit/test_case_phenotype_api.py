"""Unit tests for case_phenotype API endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

from monarch_py.api.case_phenotype import validate_disease_id, _is_disease_entity
from monarch_py.api.main import app


# =====================================================================
# Tests for validate_disease_id
# =====================================================================


@pytest.mark.parametrize(
    "input_id",
    ["MONDO:0007078", "mondo:0007078", "MONDO_0007078", "  MONDO:0007078  "],
    ids=["canonical", "lowercase", "underscore", "whitespace"],
)
def test_validate_disease_id_normalizes(input_id):
    assert validate_disease_id(input_id) == "MONDO:0007078"


@pytest.mark.parametrize(
    "input_id",
    ["", "HP:0001234", "MONDO:123", "MONDO:12345678"],
    ids=["empty", "wrong-prefix", "too-short", "too-long"],
)
def test_validate_disease_id_rejects_invalid(input_id):
    with pytest.raises(HTTPException) as exc_info:
        validate_disease_id(input_id)
    assert exc_info.value.status_code == 422


# =====================================================================
# Tests for _is_disease_entity
# =====================================================================


def _make_entity_with_category(category):
    """Helper to create a MagicMock entity with a given category."""
    if category is _SENTINEL_NO_ATTR:
        return MagicMock(spec=[])  # No category attribute
    entity = MagicMock()
    entity.category = category
    return entity


_SENTINEL_NO_ATTR = object()


@pytest.mark.parametrize(
    "category,expected",
    [
        ("biolink:Disease", True),
        (["biolink:Disease", "biolink:NamedThing"], True),
        ("biolink:DiseaseOrPhenotypicFeature", True),
        ("biolink:Gene", False),
        (_SENTINEL_NO_ATTR, False),
        (None, False),
    ],
    ids=["string", "list", "disease-or-phenotypic", "non-disease", "no-attr", "none"],
)
def test_is_disease_entity(category, expected):
    entity = _make_entity_with_category(category)
    assert _is_disease_entity(entity) is expected


# =====================================================================
# Tests for GET /case-phenotype-matrix/{disease_id} endpoint
# =====================================================================


@pytest.fixture
def client():
    return TestClient(app)


def test_case_phenotype_matrix_valid_disease(client):
    from monarch_py.implementations.solr.solr_implementation import SolrImplementation
    from monarch_py.datamodels.model import CasePhenotypeMatrixResponse

    mock_entity = MagicMock()
    mock_entity.category = "biolink:Disease"

    mock_response = CasePhenotypeMatrixResponse(
        disease_id="MONDO:0007078",
        disease_name="Achondroplasia",
        total_cases=2,
        total_phenotypes=5,
        cases=[],
        phenotypes=[],
        bins=[],
        cells={},
    )

    with (
        patch.object(SolrImplementation, "get_entity", return_value=mock_entity),
        patch.object(SolrImplementation, "get_case_phenotype_matrix", return_value=mock_response),
    ):
        response = client.get("/v3/api/case-phenotype-matrix/MONDO:0007078")
        assert response.status_code == 200
        data = response.json()
        assert data["disease_id"] == "MONDO:0007078"


def test_case_phenotype_matrix_invalid_id(client):
    response = client.get("/v3/api/case-phenotype-matrix/INVALID")
    assert response.status_code == 422


def test_case_phenotype_matrix_not_found(client):
    from monarch_py.implementations.solr.solr_implementation import SolrImplementation

    with patch.object(SolrImplementation, "get_entity", return_value=None):
        response = client.get("/v3/api/case-phenotype-matrix/MONDO:9999999")
        assert response.status_code == 404


def test_case_phenotype_matrix_non_disease(client):
    from monarch_py.implementations.solr.solr_implementation import SolrImplementation

    mock_entity = MagicMock()
    mock_entity.category = "biolink:Gene"

    with patch.object(SolrImplementation, "get_entity", return_value=mock_entity):
        response = client.get("/v3/api/case-phenotype-matrix/MONDO:0007078")
        assert response.status_code == 400
        assert "not a disease" in response.json()["detail"].lower()


def test_case_phenotype_matrix_limit_exceeded(client):
    from monarch_py.implementations.solr.solr_implementation import SolrImplementation

    mock_entity = MagicMock()
    mock_entity.category = "biolink:Disease"

    with (
        patch.object(SolrImplementation, "get_entity", return_value=mock_entity),
        patch.object(SolrImplementation, "get_case_phenotype_matrix", side_effect=ValueError("exceeds limit")),
    ):
        response = client.get("/v3/api/case-phenotype-matrix/MONDO:0007078")
        assert response.status_code == 400
