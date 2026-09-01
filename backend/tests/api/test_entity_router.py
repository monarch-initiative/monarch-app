from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from monarch_py.api.entity import router
from monarch_py.datamodels.model import Node
from monarch_py.datamodels.category_enums import AssociationCategory

client = TestClient(router)


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_entity")
def test_entity(mock_get_entity, node):
    mock_get_entity.return_value = Node(**node)
    client.get("/MONDO:0019391")
    mock_get_entity.assert_called_with("MONDO:0019391", extra=True)


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_association_table")
def test_association_table(mock_get_assoc_table):
    mock_get_assoc_table.return_value = MagicMock()
    client.get("/MONDO:0019391/biolink:DiseaseToPhenotypicFeatureAssociation")
    mock_get_assoc_table.assert_called_with(
        entity="MONDO:0019391",
        # The path param is a section *key*, not an AssociationCategory: a section can
        # combine several categories (LOINC) or span them (MEDIC+CTD), so it reaches the
        # implementation as a plain string. Legacy sections key on their category, which is
        # why this value is unchanged. This assertion was passing an enum until now only
        # because the API suite could not be collected when that change was made.
        category=AssociationCategory.DISEASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION.value,
        q=None,
        traverse_orthologs=False,
        direct=False,
        facet_fields=None,
        facet_queries=None,
        filter_queries=None,
        sort=None,
        offset=0,
        limit=20,
    )
