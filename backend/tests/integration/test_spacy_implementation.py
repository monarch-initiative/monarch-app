import pytest

from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.implementations.spacy.spacy_implementation import SpacyImplementation


def test_get_entities():
    spacy = SpacyImplementation()
    spacy.init_spacy(search_engine=SolrImplementation())
    entities = spacy.get_entities("Ehlers-Danlos syndrome, Marfan syndrome, and Loeys-Dietz syndrome are all connective tissue disorders.")
    assert entities
    assert len(entities) > 0


