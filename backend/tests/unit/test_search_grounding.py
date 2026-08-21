"""Unit tests for the grounding-oriented additions to `/search`.

These deliberately avoid Solr: the whole point of the exact-match contract is that the
decision about what counts as a match is made in code we own, so it can be tested without
a live index. (The Solr-backed grounding tests skip in CI for want of a Solr service, so
anything asserted only there is effectively unverified — see #1382.)
"""

import pytest

from monarch_py.datamodels.solr import SolrQueryResult
from monarch_py.implementations.solr.solr_parsers import match_provenance, parse_search
from monarch_py.implementations.solr.solr_query_utils import (
    build_search_query,
    escape_phrase,
    exact_match_filter_query,
    subset_filter_query,
)


### Filter query construction ###


def test_subset_filter_query_quotes_literal_names():
    assert subset_filter_query(["rare"]) == '(subsets:"rare")'


def test_subset_filter_query_ors_multiple_subsets():
    assert subset_filter_query(["rare", "otar"]) == '(subsets:"rare" OR subsets:"otar")'


def test_subset_filter_query_passes_trailing_star_through_unquoted():
    """A quoted wildcard is a literal in Lucene, so the prefix form has to stay bare."""
    assert subset_filter_query(["venom_*"]) == "(subsets:venom_*)"


def test_subset_filter_query_negates_when_excluding():
    assert subset_filter_query(["venom_*"], exclude=True) == "-(subsets:venom_*)"


def test_subset_filter_query_excludes_the_whole_disjunction():
    """`-(a OR b)` drops either; `-a OR b` would keep everything matching b."""
    assert subset_filter_query(["venom_equine", "venom_exotics"], exclude=True) == (
        '-(subsets:"venom_equine" OR subsets:"venom_exotics")'
    )


def test_exact_match_filter_query_targets_the_grounding_copy_fields():
    fq = exact_match_filter_query("septic shock")
    assert fq == 'name_grounding:"septic shock" OR synonym_grounding:"septic shock"'


@pytest.mark.parametrize(
    "value,expected",
    [
        ('say "what"', 'say \\"what\\"'),
        ("back\\slash", "back\\\\slash"),
        ("colons: are fine", "colons: are fine"),
    ],
)
def test_escape_phrase_escapes_only_what_can_break_a_phrase(value, expected):
    assert escape_phrase(value) == expected


### build_search_query ###


def test_search_query_requests_the_score():
    """`score` is a pseudo-field: without an explicit fl Solr omits it and every
    SearchResult comes back with score=None."""
    assert build_search_query(q="fanconi").fl == "*,score"


def test_search_query_adds_subset_filters():
    query = build_search_query(q="glaucoma", subset=["rare"], exclude_subset=["venom_*"])
    assert '(subsets:"rare")' in query.filter_queries
    assert "-(subsets:venom_*)" in query.filter_queries


def test_search_query_adds_taxon_curie_filter():
    query = build_search_query(q="brca", in_taxon=["NCBITaxon:9606"])
    assert 'in_taxon:"NCBITaxon:9606"' in query.filter_queries


def test_search_query_adds_exact_filter_only_when_asked():
    plain = build_search_query(q="septic shock")
    exact = build_search_query(q="septic shock", exact=True)
    assert not any("name_grounding" in fq for fq in plain.filter_queries)
    assert any("name_grounding" in fq for fq in exact.filter_queries)


def test_search_query_skips_exact_filter_for_blank_search():
    """`*:*` is a browse, not a claim that some entity is named `*:*`."""
    query = build_search_query(q="*:*", exact=True)
    assert not any("name_grounding" in fq for fq in query.filter_queries)


### match provenance ###


@pytest.mark.parametrize(
    "doc,expected",
    [
        ({"name": "septic shock"}, ("name", "exact")),
        ({"name": "Septic Shock"}, ("name", "exact")),
        ({"name": " septic shock "}, ("name", "exact")),
        ({"name": "shock", "exact_synonym": ["septic shock"]}, ("exact_synonym", "exact")),
        ({"name": "shock", "narrow_synonym": ["septic shock"]}, ("narrow_synonym", "synonym")),
        ({"name": "shock", "broad_synonym": ["septic shock"]}, ("broad_synonym", "synonym")),
        ({"name": "shock", "related_synonym": ["septic shock"]}, ("related_synonym", "synonym")),
        ({"name": "septic shock, non-human animal"}, (None, None)),
        ({"name": "shock"}, (None, None)),
    ],
)
def test_match_provenance(doc, expected):
    assert match_provenance("septic shock", doc) == expected


def test_match_provenance_prefers_name_over_synonym():
    doc = {"name": "septic shock", "exact_synonym": ["septic shock"]}
    assert match_provenance("septic shock", doc) == ("name", "exact")


@pytest.mark.parametrize("q", [None, "", "   ", "*:*"])
def test_match_provenance_declines_to_guess_without_a_query(q):
    assert match_provenance(q, {"name": "septic shock"}) == (None, None)


def test_match_provenance_tolerates_single_valued_synonym_fields():
    """`synonyms` is single-valued in the KG schema, so a str can turn up where a list is
    expected; that should not raise."""
    assert match_provenance("septic shock", {"name": "shock", "exact_synonym": "septic shock"}) == (
        "exact_synonym",
        "exact",
    )


### parse_search ###


def _query_result(docs):
    return {
        "responseHeader": {"QTime": 1, "params": {}},
        "response": {"numFound": len(docs), "start": 0, "docs": docs},
        "facet_counts": {"facet_fields": {}, "facet_queries": {}},
    }


def _parse(docs, **kwargs):
    return parse_search(SolrQueryResult(**_query_result(docs)), **kwargs)


NAMED = {"id": "MONDO:1", "category": "biolink:Disease", "name": "septic shock"}
SYNONYM = {
    "id": "MONDO:2",
    "category": "biolink:Disease",
    "name": "shock",
    "exact_synonym": ["septic shock"],
}
NARROW = {
    "id": "MONDO:3",
    "category": "biolink:Disease",
    "name": "shock, unspecified",
    "narrow_synonym": ["septic shock"],
}
VETERINARY = {
    "id": "MONDO:4",
    "category": "biolink:Disease",
    "name": "septic shock, non-human animal",
    "subsets": ["venom_equine"],
}


def test_parse_search_annotates_provenance_in_relevance_mode():
    results = _parse([NAMED, VETERINARY], q="septic shock")
    assert [(i.matched_field, i.match_type) for i in results.items] == [
        ("name", "exact"),
        (None, None),
    ]


def test_parse_search_keeps_partial_hits_in_relevance_mode():
    """Relevance mode is still search: the near-miss is returned, just labelled."""
    assert len(_parse([VETERINARY], q="septic shock").items) == 1


def test_parse_search_exact_mode_drops_non_exact_hits():
    results = _parse([NAMED, SYNONYM, NARROW, VETERINARY], q="septic shock", exact=True)
    assert [i.id for i in results.items] == ["MONDO:1", "MONDO:2"]


def test_parse_search_exact_mode_abstains_rather_than_approximating():
    results = _parse([NARROW, VETERINARY], q="septic shock", exact=True)
    assert results.items == []
    assert results.total == 0


def test_parse_search_exact_mode_totals_the_surviving_hits():
    """numFound counts the Solr candidate set, which includes the hits exact mode then
    discards; reporting it unchanged would promise results that aren't there."""
    results = _parse([NAMED, NARROW, VETERINARY], q="septic shock", exact=True)
    assert results.total == 1


def test_parse_search_populates_score_when_solr_returns_it():
    doc = {**NAMED, "score": 59.4}
    assert _parse([doc], q="septic shock").items[0].score == pytest.approx(59.4)
