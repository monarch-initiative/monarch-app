import pytest
from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.implementations.spacy.spacy_implementation import SpacyImplementation

@pytest.fixture
def spacy_instance():
    spacy = SpacyImplementation()
    spacy.init_spacy(search_engine=SolrImplementation())
    return spacy

def test_get_entities(spacy_instance):
    entities = spacy_instance.get_entities(
        "Ehlers-Danlos syndrome, Marfan syndrome, and Loeys-Dietz syndrome are all connective tissue disorders.")
    assert entities
    assert len(entities) > 0

def test_concatenate_same_entities(spacy_instance):
    entities = spacy_instance.concatenate_same_entities([
        [0, 22, 'Ehlers-Danlos syndrome classic type,MONDO:0007522'],
        [0, 22, 'Ehlers-Danlos syndrome,MONDO:0020066'],
        [0, 22, 'spondylodysplastic Ehlers-Danlos syndrome,MONDO:0034021'],
        [24, 39, 'Marfan syndrome non-human animal,MONDO:1010296'],
        [24, 39, 'Marfan syndrome,MONDO:0007947'],
        [24, 39, 'neonatal Marfan syndrome,MONDO:0017309'],
        [45, 65, 'Loeys-Dietz syndrome 1,MONDO:0012212'],
        [45, 65, 'Loeys-Dietz syndrome 2,MONDO:0012427'],
        [45, 65, 'Loeys-Dietz syndrome,MONDO:0018954'],
        [74, 101, 'connective tissue disorder non-human animal,MONDO:1011309'],
        [74, 101, 'connective tissue disorder,MONDO:0003900'],
        [74, 101, 'hereditary disorder of connective tissue,MONDO:0023603']])
    assert entities
    assert len(entities) > 0

def test_replace_entities(spacy_instance):
    result = spacy_instance.replace_entities(
        "Ehlers-Danlos syndrome, Marfan syndrome, and Loeys-Dietz syndrome are all connective tissue disorders.", [
            [0, 22,
             '|Ehlers-Danlos syndrome classic type,MONDO:0007522|Ehlers-Danlos syndrome,MONDO:0020066|spondylodysplastic Ehlers-Danlos syndrome,MONDO:0034021'],
            [24, 39,
             '|Marfan syndrome non-human animal,MONDO:1010296|Marfan syndrome,MONDO:0007947|neonatal Marfan syndrome,MONDO:0017309'],
            [45, 65,
             '|Loeys-Dietz syndrome 1,MONDO:0012212|Loeys-Dietz syndrome 2,MONDO:0012427|Loeys-Dietz syndrome,MONDO:0018954'],
            [74, 101,
             '|connective tissue disorder non-human animal,MONDO:1011309|connective tissue disorder,MONDO:0003900|hereditary disorder of connective tissue,MONDO:0023603']])
    assert result

def test_convert_to_json(spacy_instance):
    result = spacy_instance.convert_to_json(
        '<span class="sciCrunchAnnotation" data-sciGraph="|Ehlers-Danlos syndrome classic type,MONDO:0007522|Ehlers-Danlos syndrome,MONDO:0020066|spondylodysplastic Ehlers-Danlos syndrome,MONDO:0034021">Ehlers-Danlos syndrome</span>, <span class="sciCrunchAnnotation" data-sciGraph="|Marfan syndrome non-human animal,MONDO:1010296|Marfan syndrome,MONDO:0007947|neonatal Marfan syndrome,MONDO:0017309">Marfan syndrome</span>, and <span class="sciCrunchAnnotation" data-sciGraph="|Loeys-Dietz syndrome 1,MONDO:0012212|Loeys-Dietz syndrome 2,MONDO:0012427|Loeys-Dietz syndrome,MONDO:0018954">Loeys-Dietz syndrome</span> are all <span class="sciCrunchAnnotation" data-sciGraph="|connective tissue disorder non-human animal,MONDO:1011309|connective tissue disorder,MONDO:0003900|hereditary disorder of connective tissue,MONDO:0023603">connective tissue disorders</span>')
    assert result
