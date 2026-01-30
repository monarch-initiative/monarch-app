"""Tests for case-phenotype matrix construction."""
import pytest
from monarch_py.utils.case_phenotype_utils import build_matrix
from monarch_py.datamodels.model import (
    CasePhenotypeMatrixResponse,
    CaseEntity,
)


class TestBuildMatrix:
    """Test matrix construction from Solr documents."""

    @pytest.fixture
    def sample_case_docs(self):
        """Sample CaseToDiseaseAssociation documents."""
        return [
            {
                "subject": "MONARCH:case1",
                "subject_label": "Patient 1",
                "object": "MONDO:0007078",
                "object_label": "Achondroplasia",
            },
            {
                "subject": "MONARCH:case2",
                "subject_label": "Patient 2",
                "object": "MONDO:0007078",
                "object_label": "Achondroplasia",
            },
        ]

    @pytest.fixture
    def sample_phenotype_docs(self):
        """Sample CaseToPhenotypicFeatureAssociation documents."""
        return [
            {
                "subject": "MONARCH:case1",
                "object": "HP:0001250",
                "object_label": "Seizure",
                "object_closure": ["HP:0001250", "UPHENO:0004523"],
                "negated": False,
                "publications": ["PMID:12345"],
            },
            {
                "subject": "MONARCH:case1",
                "object": "HP:0000001",
                "object_label": "Another phenotype",
                "object_closure": ["HP:0000001", "UPHENO:0002964"],
                "negated": None,
            },
            {
                "subject": "MONARCH:case2",
                "object": "HP:0001250",
                "object_label": "Seizure",
                "object_closure": ["HP:0001250", "UPHENO:0004523"],
            },
        ]

    @pytest.fixture
    def sample_facet_counts(self):
        """Sample facet query results."""
        return {
            'object_closure:"UPHENO:0004523"': 2,
            'object_closure:"UPHENO:0002964"': 1,
        }

    def test_empty_input(self):
        """Empty docs should produce empty matrix."""
        result = build_matrix(
            disease_id="MONDO:0007078",
            disease_name="Test Disease",
            case_docs=[],
            phenotype_docs=[],
            facet_counts={},
        )
        assert result.total_cases == 0
        assert result.total_phenotypes == 0
        assert result.cells == {}

    def test_case_extraction(self, sample_case_docs, sample_phenotype_docs, sample_facet_counts):
        """Should extract unique cases from documents."""
        result = build_matrix(
            disease_id="MONDO:0007078",
            disease_name="Achondroplasia",
            case_docs=sample_case_docs,
            phenotype_docs=sample_phenotype_docs,
            facet_counts=sample_facet_counts,
        )
        assert result.total_cases == 2
        case_ids = [c.id for c in result.cases]
        assert "MONARCH:case1" in case_ids
        assert "MONARCH:case2" in case_ids

    def test_phenotype_deduplication(self, sample_case_docs, sample_phenotype_docs, sample_facet_counts):
        """Should deduplicate phenotypes across cases."""
        result = build_matrix(
            disease_id="MONDO:0007078",
            disease_name="Achondroplasia",
            case_docs=sample_case_docs,
            phenotype_docs=sample_phenotype_docs,
            facet_counts=sample_facet_counts,
        )
        phenotype_ids = [p.id for p in result.phenotypes]
        assert phenotype_ids.count("HP:0001250") == 1
        assert result.total_phenotypes == 2

    def test_cell_creation(self, sample_case_docs, sample_phenotype_docs, sample_facet_counts):
        """Should create cells for each case-phenotype pair."""
        result = build_matrix(
            disease_id="MONDO:0007078",
            disease_name="Achondroplasia",
            case_docs=sample_case_docs,
            phenotype_docs=sample_phenotype_docs,
            facet_counts=sample_facet_counts,
        )
        assert "MONARCH:case1:HP:0001250" in result.cells
        cell = result.cells["MONARCH:case1:HP:0001250"]
        assert cell.present is True
        assert cell.publications == ["PMID:12345"]

    def test_negated_phenotype(self, sample_case_docs, sample_facet_counts):
        """Should handle negated phenotypes."""
        phenotype_docs = [
            {
                "subject": "MONARCH:case1",
                "object": "HP:0001250",
                "object_label": "Seizure",
                "object_closure": ["HP:0001250", "UPHENO:0004523"],
                "negated": True,
            },
        ]
        result = build_matrix(
            disease_id="MONDO:0007078",
            disease_name="Test",
            case_docs=sample_case_docs[:1],
            phenotype_docs=phenotype_docs,
            facet_counts=sample_facet_counts,
        )
        cell = result.cells["MONARCH:case1:HP:0001250"]
        assert cell.negated is True

    def test_phenotype_bin_assignment(self, sample_case_docs, sample_phenotype_docs, sample_facet_counts):
        """Should assign phenotypes to correct bins based on closure."""
        result = build_matrix(
            disease_id="MONDO:0007078",
            disease_name="Achondroplasia",
            case_docs=sample_case_docs,
            phenotype_docs=sample_phenotype_docs,
            facet_counts=sample_facet_counts,
        )
        seizure = next(p for p in result.phenotypes if p.id == "HP:0001250")
        assert seizure.bin_id == "UPHENO:0004523"

    def test_bin_counts_from_facets(self, sample_case_docs, sample_phenotype_docs, sample_facet_counts):
        """Should use facet counts for bin totals."""
        result = build_matrix(
            disease_id="MONDO:0007078",
            disease_name="Achondroplasia",
            case_docs=sample_case_docs,
            phenotype_docs=sample_phenotype_docs,
            facet_counts=sample_facet_counts,
        )
        nervous_bin = next((b for b in result.bins if b.id == "UPHENO:0004523"), None)
        assert nervous_bin is not None
        assert nervous_bin.phenotype_count == 2

    @pytest.mark.parametrize("query_disease,case_disease,expected_direct,expected_source_id", [
        ("MONDO:0007078", "MONDO:0007078", True, None),
        ("MONDO:0007078", "MONDO:0007079", False, "MONDO:0007079"),
        ("MONDO:0005071", "MONDO:0007080", False, "MONDO:0007080"),
    ])
    def test_direct_indirect_case_flag(
        self, sample_phenotype_docs, sample_facet_counts,
        query_disease, case_disease, expected_direct, expected_source_id
    ):
        """Should correctly flag cases as direct or indirect based on disease match."""
        case_docs = [
            {
                "subject": "MONARCH:case1",
                "subject_label": "Patient 1",
                "object": case_disease,
                "object_label": "Test Disease",
            },
        ]
        result = build_matrix(
            disease_id=query_disease,
            disease_name="Query Disease",
            case_docs=case_docs,
            phenotype_docs=sample_phenotype_docs[:1],
            facet_counts=sample_facet_counts,
        )
        case = result.cases[0]
        assert case.is_direct is expected_direct
        assert case.source_disease_id == expected_source_id
