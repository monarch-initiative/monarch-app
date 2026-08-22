"""Unit tests for the grounding-oriented additions to `/search`.

These deliberately avoid Solr: the whole point of the exact-match contract is that the
decision about what counts as a match is made in code we own, so it can be tested without
a live index. (The Solr-backed grounding tests skip in CI for want of a Solr service, so
anything asserted only there is effectively unverified — see #1382.)
"""

import pytest

from monarch_py.api.additional_models import (
    ALL_FACET_VALUES,
    ALL_SEARCH_FACET_FIELDS,
    DEFAULT_SEARCH_FACET_FIELDS,
)
from monarch_py.datamodels.search_scopes import (
    SCOPED_AXES,
    SEARCH_SCOPES,
    SearchScope,
    resolve_scope,
)
from monarch_py.datamodels.solr import SolrQueryResult
from monarch_py.implementations.solr.solr_parsers import match_provenance, parse_search
from monarch_py.implementations.solr.solr_query_utils import (
    build_search_query,
    escape_phrase,
    escape_term,
    exact_name_filter_query,
    exact_synonym_candidate_filter_query,
    id_filter_query,
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


def test_exact_name_filter_targets_the_grounding_copy_field():
    """A hit here *is* an exact name match, so nothing needs to re-check it in Python."""
    assert exact_name_filter_query("septic shock") == 'name_grounding:"septic shock"'


def test_exact_synonym_candidates_exclude_the_name_matches():
    """Excluding them is what keeps the set Python inspects small — 15 rows against 1,744
    name matches for the worst collision in the index."""
    fq = exact_synonym_candidate_filter_query("FP")
    assert fq == 'synonym_grounding:"FP" AND -name_grounding:"FP"'


def test_id_filter_query_can_opt_out_of_the_filter_cache():
    assert id_filter_query(["MONDO:1"], cache=False) == '{!cache=false}id:"MONDO:1"'
    assert id_filter_query(["MONDO:1"]) == 'id:"MONDO:1"'


def test_id_filter_query_escapes_ids():
    assert id_filter_query(['MONDO:1"']) == 'id:"MONDO:1\\""'


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


def test_search_query_adds_exact_filter_only_when_given_one():
    plain = build_search_query(q="septic shock")
    exact = build_search_query(q="septic shock", exact_filter=exact_name_filter_query("septic shock"))
    assert not any("name_grounding" in fq for fq in plain.filter_queries)
    assert any("name_grounding" in fq for fq in exact.filter_queries)


def test_search_query_leaves_a_blank_search_alone():
    """`*:*` is a browse, not a claim that some entity is named `*:*`; SolrImplementation
    short-circuits it before ever building an exact filter."""
    query = build_search_query(q="*:*")
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


### Regressions from the #1394 review ###


def test_escape_term_escapes_whitespace_and_operators():
    """An unescaped space ends the term and the remainder becomes a clause against the
    default field, which the entity core doesn't define — Solr answers 400 and the
    endpoint 500s."""
    assert escape_term("gard rare") == "gard\\ rare"


def test_subset_wildcard_cannot_inject_a_clause():
    fq = subset_filter_query(["a) OR name:x*"])
    assert fq == "(subsets:a\\)\\ OR\\ name\\:x*)"


def test_subset_wildcard_still_works_for_ordinary_prefixes():
    assert subset_filter_query(["venom_*"]) == "(subsets:venom_*)"


def test_exact_match_filter_query_strips_the_query():
    """`name_grounding` is a KeywordTokenizer field, so padding is part of the term: an
    unstripped query finds no candidates at all for text match_provenance calls exact."""
    assert exact_name_filter_query("  Septic shock ") == 'name_grounding:"Septic shock"'


def test_exact_filter_and_provenance_agree_on_padding():
    """The two halves of the exact contract have to normalise the same way, or the filter
    excludes candidates the scope check would accept."""
    padded = "  septic shock  "
    assert exact_name_filter_query(padded) == exact_name_filter_query(padded.strip())
    assert match_provenance(padded, {"name": "septic shock"}) == ("name", "exact")


### Named scopes ###


def test_scope_expands_to_its_filters():
    assert resolve_scope(SearchScope.HUMAN_DISEASE) == {
        "category": ["biolink:Disease"],
        "namespace": ["MONDO"],
        "exclude_subset": ["venom_*"],
    }


def test_human_disease_needs_both_namespace_and_subset_exclusion():
    """VeNom terms are MONDO terms, so restricting the namespace does not drop them."""
    scope = resolve_scope(SearchScope.HUMAN_DISEASE)
    assert scope["namespace"] == ["MONDO"]
    assert scope["exclude_subset"] == ["venom_*"]


def test_human_gene_scopes_by_taxon_not_namespace():
    """A human gene recorded under a namespace other than HGNC should still qualify."""
    scope = resolve_scope(SearchScope.HUMAN_GENE)
    assert scope["in_taxon"] == ["NCBITaxon:9606"]
    assert "namespace" not in scope


def test_scope_accepts_a_bare_string():
    assert resolve_scope("human_phenotype")["namespace"] == ["HP"]


def test_explicit_argument_overrides_one_axis_of_a_scope():
    """Overriding should narrow the axis you named, not intersect into nothing."""
    resolved = resolve_scope(SearchScope.HUMAN_DISEASE, namespace=["DOID"])
    assert resolved["namespace"] == ["DOID"]
    assert resolved["category"] == ["biolink:Disease"]
    assert resolved["exclude_subset"] == ["venom_*"]


def test_no_scope_passes_explicit_arguments_through():
    assert resolve_scope(None, category=["biolink:Gene"]) == {"category": ["biolink:Gene"]}


def test_no_scope_drops_empty_arguments():
    assert resolve_scope(None, category=None, namespace=[]) == {}


def test_every_scope_is_documented():
    """The description is the contract; a scope without one can't be reasoned about."""
    for scope in SearchScope:
        assert SEARCH_SCOPES[scope].description


def test_every_scope_constrains_something():
    for scope, definition in SEARCH_SCOPES.items():
        axes = definition.category + definition.namespace + definition.subset
        axes += definition.exclude_subset + definition.in_taxon
        assert axes, f"{scope} filters nothing"


### namespace filters ###


def test_search_query_adds_namespace_filter():
    query = build_search_query(q="x", namespace=["MONDO", "HP"])
    assert 'namespace:"MONDO" OR namespace:"HP"' in query.filter_queries


def test_search_query_negates_the_whole_namespace_disjunction():
    query = build_search_query(q="x", exclude_namespace=["MPATH", "ZP"])
    assert '-(namespace:"MPATH" OR namespace:"ZP")' in query.filter_queries


### Regressions from the second #1394 review ###


def test_taxon_filters_are_escaped_like_the_namespace_ones():
    """An unbalanced quote here reached Solr as a malformed fq -> 400 -> 500."""
    query = build_search_query(q="x", in_taxon=['NCBITaxon:9606"'], in_taxon_label=['Homo "sapiens"'])
    assert 'in_taxon:"NCBITaxon:9606\\""' in query.filter_queries
    assert 'in_taxon_label:"Homo \\"sapiens\\""' in query.filter_queries


def test_facet_limit_defaults_to_solr_behaviour():
    assert build_search_query(q="x").facet_limit is None


def test_facet_limit_is_forwarded_to_solr():
    """Solr caps facet values at 100 by default, which truncates `subsets` (157 values)."""
    query = build_search_query(q="x", facet_fields=["subsets"], facet_limit=-1)
    assert query.facet_limit == -1
    assert "facet.limit=-1" in query.query_string()


def test_all_facet_values_is_unbounded():
    assert ALL_FACET_VALUES == -1


def test_facet_switch_covers_every_filterable_axis():
    """`facets=true` promises "every field you can filter on"; if a filter is added without
    a matching facet, the switch quietly stops answering the question it exists for."""
    assert set(ALL_SEARCH_FACET_FIELDS) == {
        "category",
        "in_taxon",
        "in_taxon_label",
        "namespace",
        "subsets",
    }
    assert set(DEFAULT_SEARCH_FACET_FIELDS) <= set(ALL_SEARCH_FACET_FIELDS)


### Regressions from the third #1394 review ###


def test_exact_mode_neutralises_the_query_text():
    """The filter already determines the candidate set, so leaving the raw text as the
    edismax `q` can only subtract. With q.op=AND and mm=100%, uppercased NER output like
    "…, NOT Otherwise Specified" parses `NOT` as an operator and vetoes a true whole-string
    match — exact mode would abstain on a string differing from a stored name only by case."""
    query = build_search_query(
        q="Lymphoma, NOT Otherwise Specified",
        exact_filter=exact_name_filter_query("Lymphoma, NOT Otherwise Specified"),
    )
    assert query.q == "*:*"
    assert any("name_grounding" in fq for fq in query.filter_queries)


def test_exact_mode_still_boosts_from_the_original_text():
    """Neutralising `q` must not cost the ordering among several exact matches."""
    query = build_search_query(q="ovarian carcinoma", exact_filter=exact_name_filter_query("ovarian carcinoma"))
    assert "ovarian carcinoma" in query.boost


def test_relevance_mode_leaves_the_query_alone():
    assert build_search_query(q="ovarian carcinoma").q == "ovarian carcinoma"


def test_scope_resolution_carries_axes_no_scope_sets():
    """The echo claims to be the filters actually applied. If it omits an axis the caller
    passed, replaying it gives a different answer than the request that produced it."""
    resolved = resolve_scope("human_phenotype", exclude_namespace=["HP"], in_taxon_label=["Homo sapiens"])
    assert resolved["exclude_namespace"] == ["HP"]
    assert resolved["in_taxon_label"] == ["Homo sapiens"]
    assert resolved["category"] == ["biolink:PhenotypicFeature"]


def test_scoped_axes_are_the_ones_a_scope_can_set():
    for definition in SEARCH_SCOPES.values():
        for axis in ("category", "namespace", "subset", "exclude_subset", "in_taxon"):
            assert axis in SCOPED_AXES
        assert not getattr(definition, "exclude_namespace", None)


def test_exact_search_splits_name_matches_from_synonym_candidates():
    """The two halves must not overlap: if the synonym scan re-scanned the name matches,
    the set Python inspects would be the whole candidate set again (1,753 rows for `FP`
    rather than 9), which is the shape this design exists to avoid."""
    name_fq = exact_name_filter_query("FP")
    synonym_fq = exact_synonym_candidate_filter_query("FP")
    assert f"-{name_fq}" in synonym_fq
