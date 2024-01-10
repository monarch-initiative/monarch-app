import pytest
from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.implementations.spacy.spacy_implementation import SpacyImplementation


@pytest.fixture
def spacy_instance():
    spacy = SpacyImplementation()
    spacy.init_spacy(search_engine=SolrImplementation())
    return spacy


def test_annotated_entities(spacy_instance):
    entities = spacy_instance.get_annotated_entities(
        "let me tell you about Marfan syndrome, ok?"
    )
    assert entities
    assert len(entities) == 3
    assert entities[0].text == "let me tell you about"
    assert entities[1].text == "Marfan syndrome"
    assert entities[2].text == ", ok?"


def test_get_positions(spacy_instance):
    text = "and Marfan syndrome is Marfan syndrome"
    doc = spacy_instance.nlp(text)
    positions = spacy_instance.get_positions("Marfan syndrome", doc)
    assert positions
    assert len(positions) > 0
    assert positions[0].start == 4
    assert positions[0].end == 18
    assert positions[1].start == 23
    assert positions[1].end == 37


def test_non_entity_text_is_returned(spacy_instance):
    annotation_results = spacy_instance.annotate_text("and Marfan syndrome or Ehlers Danlos")
    assert annotation_results
    assert len(annotation_results) > 1
    assert annotation_results[0].text == "and"
    assert annotation_results[1].text == "Marfan syndrome"
    assert annotation_results[2].text == "or"
    assert annotation_results[3].text == "Ehlers Danlos"


@pytest.mark.skip("Will be rewritten for a slightly different method")
def test_replace_entities(spacy_instance):
    result = spacy_instance.replace_entities(
        "Ehlers-Danlos syndrome, Marfan syndrome, and Loeys-Dietz syndrome are all connective tissue disorders.",
        [
            [
                0,
                22,
                "|Ehlers-Danlos syndrome classic type,MONDO:0007522|Ehlers-Danlos syndrome,MONDO:0020066|spondylodysplastic Ehlers-Danlos syndrome,MONDO:0034021",
            ],
            [
                24,
                39,
                "|Marfan syndrome non-human animal,MONDO:1010296|Marfan syndrome,MONDO:0007947|neonatal Marfan syndrome,MONDO:0017309",
            ],
            [
                45,
                65,
                "|Loeys-Dietz syndrome 1,MONDO:0012212|Loeys-Dietz syndrome 2,MONDO:0012427|Loeys-Dietz syndrome,MONDO:0018954",
            ],
            [
                74,
                101,
                "|connective tissue disorder non-human animal,MONDO:1011309|connective tissue disorder,MONDO:0003900|hereditary disorder of connective tissue,MONDO:0023603",
            ],
        ],
    )
    assert result
