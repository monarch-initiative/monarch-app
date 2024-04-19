import pytest
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

pytestmark = pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)


def test_histopheno():
    si = SolrImplementation()
    hp = si.get_histopheno("MONDO:0020121")

    total = 0
    for k in hp.items:
        total += k.count

    assert hp.items[0].id == "UPHENO:0002816"
