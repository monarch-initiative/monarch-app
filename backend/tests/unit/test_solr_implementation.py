from unittest.mock import patch

from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.datamodels.model import Entity, PhenotypeNeighborhood


def test_get_counterpart_entities_limit():
    # Make sure that we don't accidentally end up with the default limit again
    with patch.object(SolrImplementation, "get_associations") as mock_get_associations:
        si = SolrImplementation()
        si.get_counterpart_entities("MONDO:0007947")
        assert mock_get_associations.called
        assert mock_get_associations.call_args_list[0].kwargs["limit"] == 1000


def test_get_cross_species_term_clique_non_phenotypic_feature():
    si = SolrImplementation()
    entity = Entity(id="TEST:0001", category="biolink:Disease")
    result = si._get_cross_species_term_clique(entity)
    assert result is None


def test_get_cross_species_term_clique_root_term():
    with patch.object(SolrImplementation, "get_entity") as mock_get_entity, patch.object(
        SolrImplementation, "get_counterpart_entities"
    ) as mock_get_counterpart_entities:

        si = SolrImplementation()
        entity = Entity(id="UPHENO:0001", category="biolink:PhenotypicFeature")
        parent_entity = Entity(id="UPHENO:0001", category="biolink:PhenotypicFeature")
        child_entity = Entity(id="HP:0002", category="biolink:PhenotypicFeature")
        child_entity_2 = Entity(id="MP:0004", category="biolink:PhenotypicFeature")

        mock_get_entity.return_value = parent_entity
        mock_get_counterpart_entities.return_value = [child_entity, child_entity_2]

        result = si._get_cross_species_term_clique(entity)

        assert result is not None
        assert isinstance(result, PhenotypeNeighborhood)
        assert result.parent == parent_entity
        assert result.children == [child_entity, child_entity_2]


def test_get_cross_species_term_clique_non_upheno_parent():
    with patch.object(SolrImplementation, "get_counterpart_entities") as mock_get_counterpart_entities:

        si = SolrImplementation()
        entity = Entity(id="ZP:0001", category="biolink:PhenotypicFeature")
        parent_entity = Entity(id="UPHENO:0001", category="biolink:PhenotypicFeature")
        child_entity = Entity(id="MP:0002", category="biolink:PhenotypicFeature")

        mock_get_counterpart_entities.side_effect = [[parent_entity], [child_entity]]

        result = si._get_cross_species_term_clique(entity)

        assert result is not None
        assert isinstance(result, PhenotypeNeighborhood)
        assert result.parent == parent_entity
        assert result.children == [child_entity]


def test_get_cross_species_term_clique_no_parent():
    with patch.object(SolrImplementation, "get_counterpart_entities") as mock_get_counterpart_entities:

        si = SolrImplementation()
        entity = Entity(id="HP:0001", category="biolink:PhenotypicFeature")

        mock_get_counterpart_entities.return_value = []

        result = si._get_cross_species_term_clique(entity)

        assert result is None
