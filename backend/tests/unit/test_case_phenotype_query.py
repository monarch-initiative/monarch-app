"""Tests for case-phenotype Solr query construction."""

import json

import pytest
from monarch_py.datamodels.grid_groupings import bin_facet_key
from monarch_py.datamodels.solr import HistoPhenoKeys
from monarch_py.implementations.solr.solr_query_utils import (
    build_case_phenotype_query,
    build_case_disease_query,
)
from monarch_py.utils.utils import escape


class TestBuildCasePhenotypeQuery:
    """Test Solr query construction for case-phenotype matrix."""

    @pytest.mark.parametrize(
        "direct_only,expected_field,unexpected_field",
        [
            (True, f'object:"{escape("MONDO:0007078")}"', "object_closure"),
            (False, f'object_closure:"{escape("MONDO:0007078")}"', None),
        ],
    )
    def test_direct_vs_all_cases_query(self, direct_only, expected_field, unexpected_field):
        """Query should use correct object field based on direct_only flag."""
        params = build_case_phenotype_query(
            disease_id="MONDO:0007078",
            direct_only=direct_only,
        )
        fq = " ".join(params["fq"])
        assert expected_field in fq
        assert "{!join from=subject to=subject}" in fq
        if unexpected_field:
            assert unexpected_field not in fq

    @pytest.mark.parametrize(
        "disease_id",
        [
            "MONDO:0007078",
            "MONDO:0005071",
            "MONDO:0000001",
        ],
    )
    def test_disease_id_in_query(self, disease_id):
        """Query should include the escaped disease ID."""
        params = build_case_phenotype_query(disease_id=disease_id, direct_only=True)
        assert escape(disease_id) in " ".join(params["fq"])

    def test_filter_query_present(self):
        """Should filter to CaseToPhenotypicFeatureAssociation."""
        params = build_case_phenotype_query(
            disease_id="MONDO:0007078",
            direct_only=True,
        )
        assert 'category:"biolink:CaseToPhenotypicFeatureAssociation"' in params["fq"]

    def test_bin_facet_for_all_bins(self):
        """Should include a bin facet for every HistoPheno bin."""
        params = build_case_phenotype_query(
            disease_id="MONDO:0007078",
            direct_only=True,
        )
        facet = json.loads(params["json.facet"])
        assert len(facet) == len(HistoPhenoKeys)
        for index, key in enumerate(HistoPhenoKeys):
            assert facet[bin_facet_key(index)]["q"] == f'object_closure:"{key.value}"'

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
            "negated",
        ]
        for field in required_fields:
            assert field in fl, f"Missing required field: {field}"

    def test_closure_not_requested_per_association(self):
        """The closure describes the phenotype, not the edge. Requesting it per
        association re-sent the same ancestor lists once per edge and was ~94% of the
        response body; bins come from a JSON facet instead."""
        params = build_case_phenotype_query(disease_id="MONDO:0007078", direct_only=True)
        assert "object_closure" not in params["fl"]

    def test_bin_facet_returns_the_phenotypes_in_each_bin(self):
        """Each bin facet carries the phenotypes it contains, which is what replaced
        scanning `object_closure` on every association."""
        params = build_case_phenotype_query(
            disease_id="MONDO:0007078",
            direct_only=True,
        )
        facet = json.loads(params["json.facet"])
        for bin_facet in facet.values():
            assert "object_closure:" in bin_facet["q"]
            assert bin_facet["facet"]["entities"]["field"] == "object"

    def test_join_query_structure(self):
        """Query should have proper JOIN structure."""
        params = build_case_phenotype_query(
            disease_id="MONDO:0007078",
            direct_only=True,
        )
        # The join is an `fq`, not the `q`. Only in `fq` is it filterCache-eligible;
        # in `q` it was re-executed on every request, since these result sets exceed
        # solrconfig's queryResultMaxDocsCached.
        assert params["q"] == "*:*"
        fq = " ".join(params["fq"])
        # Should have join from subject to subject
        assert "{!join from=subject to=subject}" in fq
        # Should filter to CaseToDiseaseAssociation in the inner query
        assert 'category:"biolink:CaseToDiseaseAssociation"' in fq


class TestBuildCaseDiseaseQuery:
    """Test Solr query construction for case-disease lookup."""

    @pytest.mark.parametrize(
        "direct_only,expected_field",
        [
            (True, "object:"),
            (False, "object_closure:"),
        ],
    )
    def test_direct_vs_all_query(self, direct_only, expected_field):
        """Query should use correct object field based on direct_only flag."""
        params = build_case_disease_query(
            disease_id="MONDO:0007078",
            direct_only=direct_only,
        )
        assert expected_field in params["q"]

    @pytest.mark.parametrize(
        "disease_id",
        [
            "MONDO:0007078",
            "MONDO:0005071",
        ],
    )
    def test_disease_id_in_query(self, disease_id):
        """Query should include the escaped disease ID."""
        params = build_case_disease_query(disease_id=disease_id, direct_only=True)
        assert escape(disease_id) in params["q"]

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
