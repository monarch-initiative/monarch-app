"""Performance benchmark tests for case-phenotype matrix."""
import time
import pytest
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

pytestmark = pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)

THRESHOLD_SMALL_DISEASE = 2.0
THRESHOLD_MEDIUM_DISEASE = 3.0


@pytest.fixture
def solr():
    return SolrImplementation()


class TestCasePhenotypePerformance:

    @pytest.mark.parametrize("disease_id,max_seconds,description", [
        ("MONDO:0007078", THRESHOLD_SMALL_DISEASE, "Achondroplasia (~85 cases)"),
    ])
    def test_direct_cases_performance(self, solr, disease_id, max_seconds, description):
        start = time.perf_counter()
        result = solr.get_case_phenotype_matrix(
            disease_id=disease_id,
            direct_only=True,
            limit=200,
        )
        elapsed = time.perf_counter() - start

        print(f"\n  {description}")
        print(f"  Cases: {result.total_cases}, Phenotypes: {result.total_phenotypes}")
        print(f"  Elapsed: {elapsed:.3f}s (threshold: {max_seconds}s)")

        assert elapsed < max_seconds

    def test_empty_disease_performance(self, solr):
        start = time.perf_counter()
        result = solr.get_case_phenotype_matrix(
            disease_id="MONDO:0000001",
            direct_only=True,
            limit=200,
        )
        elapsed = time.perf_counter() - start

        assert elapsed < 0.5
        assert result.total_cases == 0
