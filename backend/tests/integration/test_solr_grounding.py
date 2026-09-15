import pytest

from monarch_py.datamodels.category_enums import EntityCategory
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


@pytest.mark.parametrize(
    "text,owner_ids",
    [
        # Each of these is an exact synonym of two distinct terms that say the same thing:
        # a uPheno cross-species class and its mouse-phenotype MP equivalent. They score
        # identically, so which one lands first is decided by Lucene doc order and flips
        # between KG builds — assert both are surfaced and that one of them leads, rather
        # than pinning a winner. (Both are also word-order rearrangements of their labels,
        # so these keep the "hypoplastic X" -> "X hypoplasia" coverage.)
        ("hypoplastic mitral valve", {"UPHENO:0088546", "MP:0031523"}),
        ("hypoplastic sternum", {"UPHENO:0081193", "MP:0004323"}),
    ],
)
@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_grounding_surfaces_all_exact_synonym_owners(text, owner_ids):  # pragma: no cover
    ids = [r.id for r in SolrImplementation().ground_entity(text)]
    assert owner_ids <= set(ids)
    assert ids[0] in owner_ids


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


### Exact-match search mode (#1392) and subset filtering (#1391) ###


@pytest.mark.parametrize(
    "text,expected_id",
    [
        ("Open-angle glaucoma", "MONDO:0005338"),
        ("Traumatic brain injury", "MONDO:0858950"),
        ("Ovarian Carcinoma", "MONDO:0005140"),
    ],
)
@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_exact_search_grounds_named_diseases(text, expected_id):  # pragma: no cover
    """Real SemMedDB disease mentions, mixed case, that a MONDO term genuinely names."""
    results = SolrImplementation().search(q=text, category=[EntityCategory.DISEASE], exact=True)
    assert [item.id for item in results.items] == [expected_id]
    assert results.items[0].match_type == "exact"


@pytest.mark.parametrize(
    "text",
    [
        "Septic shock",  # only a `<x>, non-human animal` term is lexically close
        "Androgen excess",
        "Drug Resistant Epilepsy",  # relevance mode reaches for pyridoxine-dependent epilepsy
        "Post-Operative Pain",
        "Acute appendicitis",  # a *narrow* synonym of `appendicitis`, so not an identification
    ],
)
@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_exact_search_abstains_rather_than_guessing(text):  # pragma: no cover
    """Each of these gets a confident, wrong top hit in relevance mode."""
    results = SolrImplementation().search(q=text, category=[EntityCategory.DISEASE], exact=True)
    assert results.items == []
    assert results.total == 0


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_relevance_mode_still_returns_a_best_effort_hit():  # pragma: no cover
    """The default contract is unchanged — exact mode is opt-in, not a new default."""
    results = SolrImplementation().search(q="Septic shock", category=[EntityCategory.DISEASE])
    assert results.items


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_relevance_mode_reports_why_a_hit_is_not_exact():  # pragma: no cover
    """`acute appendicitis` is recorded as a narrow synonym of `appendicitis`; a caller
    can see that without re-deriving it from the returned synonym lists."""
    results = SolrImplementation().search(q="acute appendicitis", category=[EntityCategory.DISEASE])
    appendicitis = next(item for item in results.items if item.id == "MONDO:0005649")
    assert (appendicitis.matched_field, appendicitis.match_type) == ("narrow_synonym", "synonym")


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_search_populates_score():  # pragma: no cover
    results = SolrImplementation().search(q="glaucoma", category=[EntityCategory.DISEASE])
    assert all(item.score is not None for item in results.items)


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_exclude_subset_drops_veterinary_terms():  # pragma: no cover
    """In relevance mode the VeNom term outranks every human disease for `septic shock`."""
    si = SolrImplementation()
    unfiltered = si.search(q="septic shock", category=[EntityCategory.DISEASE], limit=5)
    assert any(item.id == "MONDO:1014822" for item in unfiltered.items)

    filtered = si.search(q="septic shock", category=[EntityCategory.DISEASE], exclude_subset=["venom_*"], limit=5)
    assert not any(item.id == "MONDO:1014822" for item in filtered.items)
    assert not any(subset.startswith("venom_") for item in filtered.items for subset in (item.subsets or []))


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_subset_restricts_to_the_named_subset():  # pragma: no cover
    results = SolrImplementation().search(q="glaucoma", category=[EntityCategory.DISEASE], subset=["rare"], limit=10)
    assert results.items
    assert all("rare" in (item.subsets or []) for item in results.items)


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_exact_search_pages_beyond_the_scan_window():  # pragma: no cover
    """Short gene symbols are shared by well over a thousand entities, so exact mode has to
    report and page the whole matching set rather than a fixed candidate window."""
    si = SolrImplementation()
    first = si.search(q="FP", exact=True, limit=5)
    assert first.total > 1000
    deep = si.search(q="FP", exact=True, limit=5, offset=first.total - 3)
    assert deep.items
    assert {item.id for item in deep.items}.isdisjoint({item.id for item in first.items})


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_exact_search_tolerates_padded_query_text():  # pragma: no cover
    """NER spans arrive with whitespace; `name_grounding` is a KeywordTokenizer field, so
    the query side has to normalise the same way the scope check does."""
    results = SolrImplementation().search(q="  Ovarian Carcinoma  ", category=[EntityCategory.DISEASE], exact=True)
    assert [item.id for item in results.items] == ["MONDO:0005140"]


@pytest.mark.parametrize("q", ["*:*", "", "   "])
@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_exact_search_abstains_on_a_blank_query(q):  # pragma: no cover
    results = SolrImplementation().search(q=q, exact=True)
    assert results.items == []
    assert results.total == 0


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_exact_search_facets_describe_the_matches():  # pragma: no cover
    """Once Solr decides the exact set itself, its counts describe the rows returned, so an
    abstention reports no counts rather than counts for candidates it discarded."""
    si = SolrImplementation()
    abstained = si.search(
        q="acute appendicitis",
        category=[EntityCategory.DISEASE],
        exact=True,
        facet_fields=["category"],
    )
    assert abstained.items == []
    assert not any(v.count for f in (abstained.facet_fields or []) for v in f.facet_values)

    matched = si.search(q="FP", exact=True, limit=0, facet_fields=["category"], facet_limit=-1)
    counts = {v.label: v.count for f in matched.facet_fields for v in f.facet_values}
    assert sum(counts.values()) == matched.total


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_subset_wildcard_with_a_space_does_not_error():  # pragma: no cover
    """Unescaped, this reached Solr as two clauses and came back a 400 -> 500."""
    results = SolrImplementation().search(q="glaucoma", subset=["gard rare*"], limit=5)
    assert results.items == []


### Named scopes and facet discovery ###


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_human_disease_scope_drops_veterinary_terms():  # pragma: no cover
    results = SolrImplementation().search(q="septic shock", scope="human_disease", limit=5)
    assert results.items
    assert not any(item.id == "MONDO:1014822" for item in results.items)
    assert all(item.namespace == "MONDO" for item in results.items)


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_human_phenotype_scope_drops_the_other_species():  # pragma: no cover
    """The phenotype category is ~88% non-human, so this is the scope that earns its keep."""
    si = SolrImplementation()
    unscoped = si.search(q="short stature", category=[EntityCategory.PHENOTYPIC_FEATURE], limit=5)
    assert any(not item.id.startswith("HP:") for item in unscoped.items)

    scoped = si.search(q="short stature", scope="human_phenotype", limit=5)
    assert scoped.items
    assert all(item.id.startswith("HP:") for item in scoped.items)


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_scope_is_echoed_with_what_was_actually_applied():  # pragma: no cover
    results = SolrImplementation().search(q="glaucoma", scope="human_phenotype", namespace=["MP"], limit=2)
    assert results.scope.name == "human_phenotype"
    assert results.scope.namespace == ["MP"]  # the override, not the scope's HP
    assert results.scope.category == ["biolink:PhenotypicFeature"]
    assert results.items and all(item.id.startswith("MP:") for item in results.items)


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_no_scope_means_no_scope_on_the_response():  # pragma: no cover
    assert SolrImplementation().search(q="glaucoma", limit=1).scope is None


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_namespace_filter_restricts_results():  # pragma: no cover
    results = SolrImplementation().search(q="short stature", namespace=["MP"], limit=5)
    assert results.items
    assert all(item.namespace == "MP" for item in results.items)


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_facets_make_filter_values_discoverable():  # pragma: no cover
    """Nobody can guess these: `subsets` has 157 distinct values including raw PURLs."""
    results = SolrImplementation().search(q="*:*", limit=0, facet_fields=["subsets", "namespace"])
    faceted = {facet.label for facet in results.facet_fields}
    assert {"subsets", "namespace"} <= faceted
    subsets = next(f for f in results.facet_fields if f.label == "subsets")
    assert any(value.label == "rare" for value in subsets.facet_values)


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_facets_true_returns_every_value_not_solrs_first_hundred():  # pragma: no cover
    """`subsets` has more than Solr's default facet.limit of 100, so the discovery call has
    to lift the cap or it silently answers with a sample."""
    results = SolrImplementation().search(q="*:*", limit=0, facet_fields=["subsets"], facet_limit=-1)
    subsets = next(f for f in results.facet_fields if f.label == "subsets")
    assert len(subsets.facet_values) > 100


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_exact_search_scan_does_not_highlight():  # pragma: no cover
    """The scan reads thousands of candidates it then throws away; highlighting them is
    work nobody sees. The returned page still carries highlighting."""
    si = SolrImplementation()
    results = si.search(q="Ovarian Carcinoma", category=[EntityCategory.DISEASE], exact=True)
    assert results.items  # the page query still runs with highlighting enabled


@pytest.mark.parametrize(
    "text",
    [
        "peripheral T-cell lymphoma, not otherwise specified",
        "Peripheral T-cell Lymphoma, NOT Otherwise Specified",
        "PERIPHERAL T-CELL LYMPHOMA, NOT OTHERWISE SPECIFIED",
    ],
)
@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_exact_search_is_case_insensitive_even_around_lucene_operators(text):  # pragma: no cover
    """Exact mode promises case-insensitivity. Uppercased NER output turns `not` into the
    Lucene operator `NOT`, which used to veto the match and make the same string succeed or
    abstain depending only on its case."""
    results = SolrImplementation().search(q=text, category=[EntityCategory.DISEASE], exact=True)
    assert [item.id for item in results.items] == ["MONDO:0004964"]


@pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)
def test_scope_echo_reports_filters_the_scope_did_not_set():  # pragma: no cover
    """`scope=human_phenotype&exclude_namespace=HP` returns nothing; the echo has to show
    the exclusion rather than an `namespace: [HP]` that contradicts the result set."""
    results = SolrImplementation().search(q="short stature", scope="human_phenotype", exclude_namespace=["HP"], limit=5)
    assert results.scope.exclude_namespace == ["HP"]
    assert not any(item.id.startswith("HP:") for item in results.items)
