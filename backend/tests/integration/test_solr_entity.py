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


def test_hierarchy_limit():
    si = SolrImplementation()
    entity = si.get_entity("MONDO:0700096", extra=True)
    assert entity.node_hierarchy
    assert len(entity.node_hierarchy.sub_classes) > 20
