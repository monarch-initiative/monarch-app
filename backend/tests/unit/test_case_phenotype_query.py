"""Tests for case-phenotype Solr query construction."""
import pytest
from monarch_py.datamodels.solr import HistoPhenoKeys
from monarch_py.implementations.solr.solr_query_utils import (
    build_case_phenotype_query,
    build_case_disease_query,
)


class TestBuildCasePhenotypeQuery:
    """Test Solr query construction for case-phenotype matrix."""

    @pytest.mark.parametrize("direct_only,expected_field,unexpected_field", [
        (True, 'object:"MONDO:0007078"', "object_closure"),
        (False, 'object_closure:"MONDO:0007078"', None),
    ])
    def test_direct_vs_all_cases_query(self, direct_only, expected_field, unexpected_field):
        """Query should use correct object field based on direct_only flag."""
        params = build_case_phenotype_query(
            disease_id="MONDO:0007078",
            direct_only=direct_only,
        )
        assert expected_field in params["q"]
        assert '{!join from=subject to=subject}' in params["q"]
        if unexpected_field:
            assert unexpected_field not in params["q"]

    @pytest.mark.parametrize("disease_id", [
        "MONDO:0007078",
        "MONDO:0005071",
        "MONDO:0000001",
    ])
    def test_disease_id_in_query(self, disease_id):
        """Query should include the specified disease ID."""
        params = build_case_phenotype_query(disease_id=disease_id, direct_only=True)
        assert disease_id in params["q"]

    def test_filter_query_present(self):
        """Should filter to CaseToPhenotypicFeatureAssociation."""
        params = build_case_phenotype_query(
            disease_id="MONDO:0007078",
            direct_only=True,
        )
        assert 'category:"biolink:CaseToPhenotypicFeatureAssociation"' in params["fq"]

    def test_facet_queries_for_all_bins(self):
        """Should include facet.query for all HistoPheno bins."""
        params = build_case_phenotype_query(
            disease_id="MONDO:0007078",
            direct_only=True,
        )
        assert params["facet"] == "true"
        assert "facet.query" in params
        # Should have one facet query per HistoPhenoKeys enum value
        assert len(params["facet.query"]) == len(HistoPhenoKeys)

    def test_high_row_limit(self):
        """Should request many rows since cases are pre-bounded."""
        params = build_case_phenotype_query(
            disease_id="MONDO:0007078",
            direct_only=True,
        )
        assert params["rows"] >= 50000

    def test_custom_row_limit(self):
        """Should allow custom row limit."""
        params = build_case_phenotype_query(
            disease_id="MONDO:0007078",
            direct_only=True,
            rows=100,
        )
        assert params["rows"] == 100

    def test_required_fields_in_fl(self):
        """Should request all fields needed for matrix construction."""
        params = build_case_phenotype_query(
            disease_id="MONDO:0007078",
            direct_only=True,
        )
        fl = params["fl"]
        required_fields = [
            "subject",
            "subject_label",
            "object",
            "object_label",
            "object_closure",
            "negated",
        ]
        for field in required_fields:
            assert field in fl, f"Missing required field: {field}"

    def test_facet_queries_use_object_closure(self):
        """Facet queries should use object_closure for bin assignment."""
        params = build_case_phenotype_query(
            disease_id="MONDO:0007078",
            direct_only=True,
        )
        for facet_query in params["facet.query"]:
            assert "object_closure:" in facet_query

    def test_join_query_structure(self):
        """Query should have proper JOIN structure."""
        params = build_case_phenotype_query(
            disease_id="MONDO:0007078",
            direct_only=True,
        )
        q = params["q"]
        # Should have join from subject to subject
        assert "{!join from=subject to=subject}" in q
        # Should filter to CaseToDiseaseAssociation in the inner query
        assert 'category:"biolink:CaseToDiseaseAssociation"' in q


class TestBuildCaseDiseaseQuery:
    """Test Solr query construction for case-disease lookup."""

    @pytest.mark.parametrize("direct_only,expected_field", [
        (True, "object:"),
        (False, "object_closure:"),
    ])
    def test_direct_vs_all_query(self, direct_only, expected_field):
        """Query should use correct object field based on direct_only flag."""
        params = build_case_disease_query(
            disease_id="MONDO:0007078",
            direct_only=direct_only,
        )
        assert expected_field in params["q"]

    @pytest.mark.parametrize("disease_id", [
        "MONDO:0007078",
        "MONDO:0005071",
    ])
    def test_disease_id_in_query(self, disease_id):
        """Query should include the specified disease ID."""
        params = build_case_disease_query(disease_id=disease_id, direct_only=True)
        assert disease_id in params["q"]

    def test_filter_query_present(self):
        """Should filter to CaseToDiseaseAssociation."""
        params = build_case_disease_query(
            disease_id="MONDO:0007078",
            direct_only=True,
        )
        assert 'category:"biolink:CaseToDiseaseAssociation"' in params["fq"]

    def test_required_fields_in_fl(self):
        """Should request fields needed for case-disease lookup."""
        params = build_case_disease_query(
            disease_id="MONDO:0007078",
            direct_only=True,
        )
        fl = params["fl"]
        required_fields = ["subject", "subject_label", "object", "object_label"]
        for field in required_fields:
            assert field in fl, f"Missing required field: {field}"

    def test_default_row_limit(self):
        """Should have high default row limit."""
        params = build_case_disease_query(
            disease_id="MONDO:0007078",
            direct_only=True,
        )
        assert params["rows"] >= 50000

    def test_custom_row_limit(self):
        """Should allow custom row limit."""
        params = build_case_disease_query(
            disease_id="MONDO:0007078",
            direct_only=True,
            rows=100,
        )
        assert params["rows"] == 100
