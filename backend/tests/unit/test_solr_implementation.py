import pytest
from unittest.mock import patch

from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.datamodels.model import Entity, CrossSpeciesTermClique


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


@pytest.mark.parametrize("prefix", SolrImplementation.CROSS_SPECIES_PREFIXES)
def test_get_cross_species_term_clique_root_term(prefix):
    with patch.object(SolrImplementation, "get_entity") as mock_get_entity, patch.object(
        SolrImplementation, "get_counterpart_entities"
    ) as mock_get_counterpart_entities:

        si = SolrImplementation()
        entity_id = f"{prefix}:0001"
        entity = Entity(id=entity_id, category="biolink:PhenotypicFeature")
        parent_entity = Entity(id=entity_id, category="biolink:PhenotypicFeature")
        child_entity = Entity(id="HP:0002", category="biolink:PhenotypicFeature")
        child_entity_2 = Entity(id="MP:0004", category="biolink:PhenotypicFeature")

        mock_get_entity.return_value = parent_entity
        mock_get_counterpart_entities.return_value = [child_entity, child_entity_2]

        result = si._get_cross_species_term_clique(entity)

        assert result is not None
        assert isinstance(result, CrossSpeciesTermClique)
        assert result.root_term == parent_entity
        assert result.entities == [child_entity, child_entity_2]


@pytest.mark.parametrize("prefix", SolrImplementation.CROSS_SPECIES_PREFIXES)
def test_get_cross_species_term_clique_child_term(prefix):
    with patch.object(SolrImplementation, "get_counterpart_entities") as mock_get_counterpart_entities:

        si = SolrImplementation()
        entity = Entity(id="ZP:0001", category="biolink:PhenotypicFeature")
        parent_entity = Entity(id=f"{prefix}:0001", category="biolink:PhenotypicFeature")
        child_entity = Entity(id="MP:0002", category="biolink:PhenotypicFeature")

        mock_get_counterpart_entities.side_effect = [[parent_entity], [child_entity]]

        result = si._get_cross_species_term_clique(entity)

        assert result is not None
        assert isinstance(result, CrossSpeciesTermClique)
        assert result.root_term == parent_entity
        assert result.entities == [child_entity]


def test_get_cross_species_term_clique_no_parent():
    with patch.object(SolrImplementation, "get_counterpart_entities") as mock_get_counterpart_entities:

        si = SolrImplementation()
        entity = Entity(id="HP:0001", category="biolink:PhenotypicFeature")

        mock_get_counterpart_entities.return_value = []

        result = si._get_cross_species_term_clique(entity)

        assert result is None
