import pytest
from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.implementations.spacy.spacy_implementation import SpacyImplementation


@pytest.fixture
def spacy_instance():
    spacy = SpacyImplementation()
    spacy.init_spacy(grounding_implementation=SolrImplementation())
    return spacy


def test_spacy_positions(spacy_instance):
    entity = spacy_instance.nlp("the brain").ents[0]
    entity.start = 4
    entity.end = 9


def test_spacy_positions_with_two_entities(spacy_instance):
    entities = spacy_instance.nlp("the brain and the heart").ents
    assert len(entities) == 2
    assert entities[0].start_char == 4
    assert entities[0].end_char == 9
    assert entities[1].start_char == 18
    assert entities[1].end_char == 23


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_entity_positions(spacy_instance):
    entities = spacy_instance.get_annotated_entities("the brain")
    assert entities
    assert len(entities) == 2
    assert entities[0].text == "the "
    assert entities[1].text == "brain"
    assert entities[1].start == 4
    assert entities[1].end == 9


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_annotated_entities(spacy_instance):
    entities = spacy_instance.get_annotated_entities("let me tell you about Marfan syndrome, ok?")
    assert entities
    assert len(entities) == 3
    assert entities[0].text == "let me tell you about "
    assert entities[1].text == "Marfan syndrome"
    assert entities[2].text == ", ok?"


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_non_entity_text_is_returned_between_entities(spacy_instance):
    entities = spacy_instance.get_annotated_entities(
        "let me tell you about Marfan syndrome and Ehlers Danlos syndrome, ok?"
    )
    assert entities
    assert len(entities) > 1
    assert entities[0].text == "let me tell you about "
    assert entities[1].text == "Marfan syndrome"
    assert entities[2].text == " and "
    assert entities[3].text == "Ehlers Danlos syndrome"
    assert entities[4].text == ", ok?"


# This test is intended to act as guard rails and documentation of entity recognition quality, if we collect
# terms that work and do not work here, we can eventually test a full list against alternate models
@pytest.mark.parametrize(
    "text",
    [
        "Marfan syndrome",
        "Ehlers-Danlos syndrome",
        # fails: "Ehlers Danlos syndrome",
        # fails: "Ehlers Danlos",
        "Loeys-Dietz syndrome",
        "connective tissue disorder",
    ],
)
def test_entity_recognition(spacy_instance, text):
    entities = spacy_instance.nlp(text).ents
    assert [entity.text for entity in entities] == [text]
