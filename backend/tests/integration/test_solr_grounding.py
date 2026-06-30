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


@pytest.mark.parametrize(
    "text,expected_id",
    [
        # multi-word exact synonyms
        ("kidney disease", "MONDO:0005240"),
        ("renal disorder", "MONDO:0005240"),
        # abbreviations
        ("DLE", "MONDO:0019558"),
        ("USH2", "MONDO:0016484"),
        # word-order rearrangements (X of Y ↔ Y X)
        ("stenosis of larynx", "MONDO:0001305"),
        ("atrophy of tongue papillae", "MONDO:0001989"),
        ("hypoplastic sternum", "UPHENO:0081193"),
    ],
)
@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_grounding_ranks_exact_synonym_first(text, expected_id):  # pragma: no cover
    matching_results = SolrImplementation().ground_entity(text)
    assert matching_results
    assert matching_results[0].id == expected_id


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_grounding_surfaces_all_exact_synonym_owners():  # pragma: no cover
    # "hypoplastic mitral valve" is an exact synonym of two distinct "mitral valve hypoplasia" terms
    # (a uPheno cross-species class and the mouse-phenotype MP term), so neither deterministically
    # ranks first — assert grounding surfaces both rather than pinning a fragile order.
    ids = {r.id for r in SolrImplementation().ground_entity("hypoplastic mitral valve")}
    assert {"UPHENO:0088546", "MP:0031523"} <= ids


@pytest.mark.parametrize(
    "text,unwanted_id",
    [
        # Regression guard from #1306: a mouse gene `Pdss2` carries "kidney disease"
        # as a synonym (its old nickname `kd`). A partial-name match on the gene
        # record used to outrank the correct disease.
        ("kidney disease", "MGI:1918615"),
    ],
)
@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_grounding_does_not_rank_partial_match_first(text, unwanted_id):  # pragma: no cover
    matching_results = SolrImplementation().ground_entity(text)
    assert matching_results
    assert matching_results[0].id != unwanted_id
