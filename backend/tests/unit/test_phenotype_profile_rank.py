"""Unit tests for the experimental phenotype profile's row ordering."""

import pytest

from monarch_py.service.phenotype_profile import frequency_score, rank_key, wilson_lower_bound


def row(label, observations=(), dismech=(), negated=False):
    r = {
        "label": label,
        "negated": negated,
        "observations": list(observations),
        "dismech": list(dismech),
        "sources": sorted({o["source"] for o in observations}),
    }
    r["frequency_score"] = frequency_score(r)
    return r


def obs(source="infores:omim", **kw):
    return {"source": source, **kw}


def dm(diagnostic=False, frequency_hp=None):
    return {"diagnostic": diagnostic, "frequency_hp": frequency_hp}


def order(*rows):
    return [r["label"] for r in sorted(rows, key=rank_key)]


def test_wilson_lower_bound_discounts_small_counts():
    assert wilson_lower_bound(1, 1) == pytest.approx(0.207, abs=0.001)
    assert wilson_lower_bound(700, 1827) > wilson_lower_bound(1, 1)
    assert wilson_lower_bound(0, 0) == 0.0


def test_single_case_ranks_below_very_frequent_band():
    assert order(
        row("one of one", [obs(count=1, total=1)]),
        row("very frequent", [obs("infores:orphanet", frequency="HP:0040281")]),
    ) == ["very frequent", "one of one"]


def test_diagnostic_first_negated_last():
    assert order(
        row("not seen", [obs(frequency="HP:0040281")], negated=True),
        row("common", [obs(frequency="HP:0040281")]),
        row("diagnostic", [obs(frequency="HP:0040283")], [dm(diagnostic=True)]),
    ) == ["diagnostic", "common", "not seen"]


def test_more_sources_win_within_a_tier():
    assert order(
        row("one source", [obs(frequency="HP:0040282")]),
        row("corroborated", [obs(frequency="HP:0040282"), obs("infores:orphanet")], [dm()]),
    ) == ["corroborated", "one source"]


def test_tier_beats_source_count():
    assert order(
        row("occasional everywhere", [obs(frequency="HP:0040283"), obs("infores:orphanet")], [dm()]),
        row("frequent once", [obs(frequency="HP:0040282")]),
    ) == ["frequent once", "occasional everywhere"]


def test_unknown_frequency_sorts_after_known():
    assert order(row("unknown", [obs()]), row("rare", [obs(frequency="HP:0040284")])) == ["rare", "unknown"]


def test_dismech_only_row_uses_dismech_frequency():
    assert row("dismech", dismech=[dm(frequency_hp="HP:0040282")])["frequency_score"] == 0.3


def test_dismech_frequency_never_overrides_kg_frequency():
    r = row("kg says occasional", [obs(frequency="HP:0040283")], [dm(frequency_hp="HP:0040281")])
    assert r["frequency_score"] == 0.05


def test_disagreeing_sources_average_down():
    agree = row("agree", [obs(frequency="HP:0040281"), obs("infores:orphanet", frequency="HP:0040281")])
    disagree = row("disagree", [obs(count=1, total=14), obs("infores:orphanet", frequency="HP:0040281")])
    assert order(disagree, agree) == ["agree", "disagree"]


def test_kg_sources_outrank_dismech_corroboration():
    assert order(
        row("orphanet and dismech", [obs("infores:orphanet", frequency="HP:0040281")], [dm()]),
        row("omim and orphanet", [obs(frequency="HP:0040281"), obs("infores:orphanet", frequency="HP:0040281")]),
        row("orphanet only", [obs("infores:orphanet", frequency="HP:0040281")]),
    ) == ["omim and orphanet", "orphanet and dismech", "orphanet only"]
