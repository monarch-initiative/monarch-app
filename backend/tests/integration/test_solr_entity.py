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
    # Verify node_hierarchy returns the full sub_class set (fetched with limit=1000), not a low cap.
    # Needs an entity with many direct subclasses; "nervous system disorder" has ~70 (the previous
    # entity, "human disease" / MONDO:0700096, was refactored down to 4 direct children).
    si = SolrImplementation()
    entity = si.get_entity("MONDO:0005071", extra=True)
    assert entity.node_hierarchy
    assert len(entity.node_hierarchy.sub_classes) > 20
