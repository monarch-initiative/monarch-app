import pytest

from monarch_py.implementations.solr.solr_implementation import SolrImplementation


@pytest.mark.parametrize(
    "text,expected_id",
    [
        ("Marfan syndrome", "MONDO:0007947"),
        ("Ehlers-Danlos syndrome", "MONDO:0020066"),
        ("Loeys-Dietz syndrome", "MONDO:0018954"),
        ("connective tissue disorder", "MONDO:0003900"),
    ],
)
@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_grounding(text, expected_id):
    matching_results = SolrImplementation().ground_entity(text)
    assert matching_results
    matching_identifiers = [result.id for result in matching_results]
    assert expected_id in matching_identifiers


@pytest.mark.parametrize(
    "text,unwanted_id",
    [
        ("patients", "MGI:1332635"),
        ("reduced", "MONDO:0012143"),
        ("Bard", "MONDO:0014432"),
    ],
)
@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_grounding_should_not_match(text, unwanted_id):
    matching_results = SolrImplementation().ground_entity(text)
    identifiers = [result.id for result in matching_results]
    assert unwanted_id not in identifiers or len(identifiers) == 0
