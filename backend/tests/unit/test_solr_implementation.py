from unittest.mock import patch, MagicMock

from monarch_py.implementations.solr.solr_implementation import SolrImplementation


def test_get_counterpart_entities_limit():
    # Make sure that we don't accidentally end up with the default limit again
    with patch.object(SolrImplementation, "get_associations") as mock_get_associations:
        si = SolrImplementation()
        si.get_counterpart_entities("MONDO:0007947")
        assert mock_get_associations.called
        assert mock_get_associations.call_args_list[0].kwargs["limit"] == 1000


def test_get_generic_entity_grid_accepts_multiple_row_categories():
    """get_generic_entity_grid should accept row_assoc_categories as a list."""
    mock_entity = MagicMock()
    mock_entity.category = "biolink:Disease"
    mock_entity.configure_mock(name="Type 2 diabetes mellitus")

    with patch.object(SolrImplementation, "get_entity", return_value=mock_entity), \
         patch.object(SolrImplementation, "_get_entity_name", return_value="Type 2 diabetes mellitus"), \
         patch.object(SolrImplementation, "_raw_solr_query") as mock_query:
        mock_query.return_value = {"response": {"docs": []}}

        si = SolrImplementation()

        # This should not raise TypeError - it should accept row_assoc_categories
        result = si.get_generic_entity_grid(
            context_id="MONDO:0005148",
            column_assoc_categories=["biolink:DiseaseToPhenotypicFeatureAssociation"],
            row_assoc_categories=[
                "biolink:DiseaseToPhenotypicFeatureAssociation",
                "biolink:CaseToPhenotypicFeatureAssociation",
            ],
        )

        # Verify the call went through
        assert result is not None
