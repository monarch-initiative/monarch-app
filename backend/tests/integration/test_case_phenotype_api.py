"""Integration tests for case-phenotype API endpoint."""
import pytest
from fastapi.testclient import TestClient
from monarch_py.api.main import app
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

pytestmark = pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)


@pytest.fixture
def client():
    return TestClient(app)


class TestCasePhenotypeEndpoint:
    """Test /v3/api/case-phenotype-matrix endpoint."""

    def test_get_matrix_success(self, client):
        response = client.get("/v3/api/case-phenotype-matrix/MONDO:0007078")
        assert response.status_code == 200
        data = response.json()
        assert "disease_id" in data
        assert data["disease_id"] == "MONDO:0007078"
        assert "cases" in data
        assert "phenotypes" in data
        assert "cells" in data
        assert "bins" in data

    def test_direct_parameter(self, client):
        response_direct = client.get("/v3/api/case-phenotype-matrix/MONDO:0007078?direct=true")
        response_all = client.get("/v3/api/case-phenotype-matrix/MONDO:0007078?direct=false")
        assert response_direct.status_code == 200
        assert response_all.status_code == 200
        direct_count = response_direct.json()["total_cases"]
        all_count = response_all.json()["total_cases"]
        assert all_count >= direct_count

    def test_limit_parameter(self, client):
        # Use a high enough limit that won't be exceeded
        response = client.get("/v3/api/case-phenotype-matrix/MONDO:0007078?limit=200")
        assert response.status_code == 200
        data = response.json()
        assert data["total_cases"] <= 200

    def test_over_limit_error(self, client):
        # Use a very small limit to ensure we exceed it
        response = client.get("/v3/api/case-phenotype-matrix/MONDO:0007078?direct=false&limit=1")
        assert response.status_code == 400
        assert "exceeds limit" in response.json()["detail"]

    def test_disease_not_found(self, client):
        response = client.get("/v3/api/case-phenotype-matrix/MONDO:9999999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_invalid_id_format(self, client):
        response = client.get("/v3/api/case-phenotype-matrix/not-a-valid-id")
        assert response.status_code == 422
        detail = response.json()["detail"].lower()
        assert "invalid" in detail or "validation" in detail

    def test_not_a_disease(self, client):
        # HP:0001250 is a phenotype, not a disease
        response = client.get("/v3/api/case-phenotype-matrix/HP:0001250")
        assert response.status_code == 422
        detail = response.json()["detail"].lower()
        assert "invalid" in detail or "mondo" in detail

    @pytest.mark.parametrize("limit,should_succeed", [
        (1, True),
        (50, True),
        (200, True),
        (1000, True),
        (0, False),
        (-1, False),
        (1001, False),
    ])
    def test_limit_validation(self, client, limit, should_succeed):
        response = client.get(f"/v3/api/case-phenotype-matrix/MONDO:0007078?limit={limit}")
        if should_succeed:
            # May succeed or fail based on actual case count
            assert response.status_code in [200, 400]
        else:
            assert response.status_code == 422

    def test_disease_with_no_cases(self, client):
        # MONDO:0000001 is "disease" - the root class, no direct cases
        response = client.get("/v3/api/case-phenotype-matrix/MONDO:0000001")
        assert response.status_code == 200
        data = response.json()
        assert data["total_cases"] == 0
        assert data["cells"] == {}

    def test_response_structure(self, client):
        response = client.get("/v3/api/case-phenotype-matrix/MONDO:0007078")
        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "disease_id" in data
        assert "disease_name" in data
        assert "total_cases" in data
        assert "total_phenotypes" in data
        assert "cases" in data
        assert "phenotypes" in data
        assert "bins" in data
        assert "cells" in data

        # Check types
        assert isinstance(data["total_cases"], int)
        assert isinstance(data["total_phenotypes"], int)
        assert isinstance(data["cases"], list)
        assert isinstance(data["phenotypes"], list)
        assert isinstance(data["bins"], list)
        assert isinstance(data["cells"], dict)

    def test_bins_have_labels(self, client):
        response = client.get("/v3/api/case-phenotype-matrix/MONDO:0007078")
        assert response.status_code == 200
        data = response.json()

        for bin in data["bins"]:
            assert "id" in bin
            assert "label" in bin
            assert "phenotype_count" in bin
