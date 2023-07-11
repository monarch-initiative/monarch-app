import pytest

from monarch_py.datamodels.model import Entity, Association
from monarch_py.implementations.solr.solr_implementation import SolrImplementation


@pytest.mark.parametrize(
    "association",
    [
        Association(
            id="uuid:0000001",
            subject="ENT:0000003",
            subject_closure=["ENT:0000001"],
            object="ENT:0000002",
            object_category="biolink:testCase",
            object_label="Test Case 2",
            predicate="ASSOC:0000001",
        ),
        Association(
            id="uuid:0000002",
            object="ENT:0000004",
            object_closure=["ENT:0000001"],
            subject="ENT:0000002",
            subject_category="biolink:testCase",
            subject_label="Test Case 2",
            predicate="ASSOC:0000002",
        ),
    ]
)
def test_get_associated_entity(association):
    """Test that the get_associated_entity function returns the correct entity"""
    entity_1 = Entity(
        id="ENT:0000001",
        name="Test Case 1",
        category="biolink:testCase",
    )
    entity_2 = Entity(
        id="ENT:0000002",
        name="Test Case 2",
        category="biolink:testCase",
    )
    si = SolrImplementation()
    associated_entity = si._get_associated_entity(association, entity_1)
    assert associated_entity == entity_2, \
        f"Associated entity is not as expected. Expected: {entity_2}, got: {associated_entity}"

