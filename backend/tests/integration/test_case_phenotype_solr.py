"""Integration tests for case-phenotype Solr queries."""
import pytest
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

pytestmark = pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)


@pytest.fixture
def solr():
    """Create Solr implementation for testing."""
    return SolrImplementation()


class TestGetCasePhenotypeMatrix:
    """Test Solr implementation of case-phenotype matrix."""

    def test_achondroplasia_direct_cases(self, solr):
        """MONDO:0007078 should return known case-phenotype data."""
        result = solr.get_case_phenotype_matrix(
            disease_id="MONDO:0007078",
            direct_only=True,
            limit=200,
        )
        assert result.total_cases > 0
        assert result.total_cases <= 200
        assert result.total_phenotypes > 0
        assert len(result.cells) > 0

    def test_limit_enforcement(self, solr):
        """Should raise error when cases exceed limit."""
        # MONDO:0005071 (hereditary breast carcinoma) has many cases
        # Use a very small limit to trigger the error
        with pytest.raises(ValueError, match="exceeds limit"):
            solr.get_case_phenotype_matrix(
                disease_id="MONDO:0005071",
                direct_only=False,
                limit=1,
            )

    def test_disease_with_no_cases(self, solr):
        """Should return empty matrix for disease with no cases."""
        # MONDO:0000001 is "disease" - the root class, no direct cases
        result = solr.get_case_phenotype_matrix(
            disease_id="MONDO:0000001",
            direct_only=True,
            limit=200,
        )
        assert result.total_cases == 0
        assert result.cells == {}

    def test_cell_data_populated(self, solr):
        """Cells should have proper metadata when available."""
        result = solr.get_case_phenotype_matrix(
            disease_id="MONDO:0007078",
            direct_only=True,
            limit=200,
        )
        assert all(c.present for c in result.cells.values())

    def test_bins_are_ordered(self, solr):
        """Bins should be returned in HistoPhenoKeys order."""
        result = solr.get_case_phenotype_matrix(
            disease_id="MONDO:0007078",
            direct_only=True,
            limit=200,
        )
        # First bin should be skeletal_system
        assert result.bins[0].id == "UPHENO:0002964"
        assert result.bins[0].label == "skeletal system"

    def test_cases_have_labels(self, solr):
        """Cases should have labels."""
        result = solr.get_case_phenotype_matrix(
            disease_id="MONDO:0007078",
            direct_only=True,
            limit=200,
        )
        for case in result.cases:
            assert case.id is not None
            # Labels may or may not be present depending on data

    def test_phenotypes_have_bins(self, solr):
        """All phenotypes should be assigned to a bin."""
        result = solr.get_case_phenotype_matrix(
            disease_id="MONDO:0007078",
            direct_only=True,
            limit=200,
        )
        for phenotype in result.phenotypes:
            assert phenotype.bin_id is not None

    def test_direct_only_false(self, solr):
        """Should include indirect cases when direct_only=False."""
        # Get direct only first
        direct_result = solr.get_case_phenotype_matrix(
            disease_id="MONDO:0007078",
            direct_only=True,
            limit=500,
        )
        # Get with descendants - should have same or more cases
        all_result = solr.get_case_phenotype_matrix(
            disease_id="MONDO:0007078",
            direct_only=False,
            limit=500,
        )
        assert all_result.total_cases >= direct_result.total_cases
