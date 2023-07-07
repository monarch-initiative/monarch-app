import pytest
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

pytestmark = pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)


def test_entity():
    si = SolrImplementation()
    entity = si.get_entity("MONDO:0007947", extra=False)
    assert entity
    assert entity.name == "Marfan syndrome"
