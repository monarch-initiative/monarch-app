import pytest
from monarch_py.datamodels.model import Association, Entity
from monarch_py.implementations.solr.solr_implementation import SolrImplementation


@pytest.mark.parametrize(
    ("association", "this_entity", "other_entity"),
    [
        (
            Association(
                id="uuid:0000001",
                subject="ENT:0000003",
                subject_category="biolink:testCase",
                subject_label="Test Case 3",
                subject_closure=["ENT:0000001"],
                object="ENT:0000002",
                object_category="biolink:testCase",
                object_label="Test Case 2",
                predicate="biolink:subclass_of",
                knowledge_level="not_provided",
                agent_type="not_provided",
            ),
            Entity(id="ENT:0000002", name="Test Case 2", category="biolink:testCase"),
            Entity(id="ENT:0000003", name="Test Case 3", category="biolink:testCase"),
        ),
        (
            Association(
                id="uuid:0000002",
                object="ENT:0000004",
                object_category="biolink:testCase",
                object_label="Test Case 4",
                object_closure=["ENT:0000001"],
                subject="ENT:0000003",
                subject_category="biolink:testCase",
                subject_label="Test Case 3",
                predicate="biolink:subclass_of",
                knowledge_level="not_provided",
                agent_type="not_provided",
            ),
            Entity(id="ENT:0000003", name="Test Case 3", category="biolink:testCase"),
            Entity(id="ENT:0000004", name="Test Case 4", category="biolink:testCase"),
        ),
    ],
)
def test_get_counterpart_entity(association, this_entity, other_entity):
    """Test that the get_counterpart_entity function returns the correct entity"""
    si = SolrImplementation()
    associated_entity = si._get_counterpart_entity(association, this_entity)
    assert (
        associated_entity == other_entity
    ), f"Associated entity is not as expected. Expected: {other_entity}, got: {associated_entity}"
