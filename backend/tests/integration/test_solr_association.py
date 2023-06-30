import pytest

from monarch_py.implementations.solr.solr_implementation import SolrImplementation

pytestmark = pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)


def test_associations():
    si = SolrImplementation()
    response = si.get_associations()
    assert response
    assert response.total > 100000
    assert len(response.items) == 20


def test_association_page_limit():
    si = SolrImplementation()
    response = si.get_associations(limit=100)
    assert len(response.items) == 100


def test_association_category():
    si = SolrImplementation()
    response = si.get_associations(
        category="biolink:CorrelatedGeneToDiseaseAssociation"
    )
    assert response
    assert response.total > 6000
    assert "biolink:CorrelatedGeneToDiseaseAssociation" in response.items[0].category


def test_association_predicate():
    si = SolrImplementation()
    response = si.get_associations(predicate="biolink:has_phenotype")
    assert response
    assert response.total > 600000
    assert "biolink:has_phenotype" in response.items[0].predicate


def test_subject():
    si = SolrImplementation()
    response = si.get_associations(subject="MONDO:0007947", direct=True)
    assert response
    assert response.total > 50
    assert response.items[0].subject == "MONDO:0007947"


def test_object():
    si = SolrImplementation()
    response = si.get_associations(object="MONDO:0007947", direct=True)
    assert response
    assert response.total > 0
    assert response.items[0].object == "MONDO:0007947"


def test_object_closure():
    si = SolrImplementation()
    response = si.get_associations(object="HP:0000240")
    assert response
    assert response.total in range(200, 10000)


def test_entity():
    si = SolrImplementation()
    response = si.get_associations(entity="MONDO:0007947")
    assert response
    assert response.total > 50
    for association in response.items:
        assert (
            "MONDO:0007947" in association.subject_closure
            or "MONDO:0007947" in association.object_closure
        )


