import pytest

from monarch_py.implementations.solr.solr_implementation import SolrImplementation


# Each row asserts: the rank-1 result is one of the acceptable IDs.
# Most cases have a single canonical ID. Word-order phenotype synonyms have
# parallel UPHENO/MP entries for the same biological concept; either is correct.
EXACT_SYNONYM_CASES = [
    ("kidney disease", {"MONDO:0005240"}),
    ("renal disorder", {"MONDO:0005240"}),
    ("stenosis of larynx", {"MONDO:0001305"}),
    ("atrophy of tongue papillae", {"MONDO:0001989"}),
    ("hypoplastic sternum", {"UPHENO:0081193", "MP:0004323"}),
    ("hypoplastic mitral valve", {"UPHENO:0088546", "MP:0031523"}),
]


@pytest.mark.parametrize("text,acceptable_ids", EXACT_SYNONYM_CASES)
@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_search_ranks_exact_synonym_first(text, acceptable_ids):
    results = SolrImplementation().search(q=text)
    assert results.items
    assert results.items[0].id in acceptable_ids


@pytest.mark.parametrize("text,acceptable_ids", EXACT_SYNONYM_CASES)
@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_autocomplete_ranks_exact_synonym_first(text, acceptable_ids):
    results = SolrImplementation().autocomplete(q=text)
    assert results.items
    assert results.items[0].id in acceptable_ids


@pytest.mark.parametrize(
    "text,unwanted_id",
    [
        # Regression guard: the gene Pdss2 has "kidney disease" as a synonym (old
        # nickname `kd`). It used to outrank the correct disease.
        ("kidney disease", "MGI:1918615"),
    ],
)
@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_search_does_not_rank_partial_match_first(text, unwanted_id):
    results = SolrImplementation().search(q=text)
    assert results.items
    assert results.items[0].id != unwanted_id
