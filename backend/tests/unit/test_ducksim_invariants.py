"""Invariant / metamorphic tests for the ducksim engine.

Unlike test_ducksim.py (which pins exact scores on one fixed KG), these assert *properties* that
must hold on any KG — the class of guarantees that catches data-shape bugs the happy-path tests miss
(e.g. duplicate associations inflating the jaccard intersection into an inf/negative denominator).

Ontology (reflexive subClassOf): A1 < A < R, B1 < B < R.  Entities are MONDO diseases so the same
KG can drive the API-contract tests.
"""

import math

import duckdb
import pytest

from monarch_py.service.ducksim import Ducksim

METRICS = ["ancestor_information_content", "jaccard_similarity", "phenodigm_score"]

# MONDO:1 is annotated to A1 twice — the multi-evidence duplicate that must not be double-counted.
DUP_ASSOC = [("MONDO:1", "A1"), ("MONDO:1", "A1"), ("MONDO:2", "B1"), ("MONDO:3", "A1")]
UNIQ_ASSOC = [("MONDO:1", "A1"), ("MONDO:2", "B1"), ("MONDO:3", "A1")]


def baked_kg(path, assoc_rows):
    """Build a tiny baked monarch-kg.duckdb and return a Ducksim over it. `assoc_rows` is a list of
    (entity, phenotype) has_phenotype edges; duplicates are allowed. IC / closure_size are baked with
    koza's count(DISTINCT) formulas."""
    con = duckdb.connect(str(path))
    con.execute("CREATE TABLE closure(subject_id VARCHAR, predicate_id VARCHAR, object_id VARCHAR)")
    con.executemany(
        "INSERT INTO closure VALUES (?, 'rdfs:subClassOf', ?)",
        [("R", "R"), ("A", "A"), ("A", "R"), ("B", "B"), ("B", "R"),
         ("A1", "A1"), ("A1", "A"), ("A1", "R"), ("B1", "B1"), ("B1", "B"), ("B1", "R")],
    )
    con.execute(
        "CREATE TABLE edges(subject VARCHAR, object VARCHAR, category VARCHAR, predicate VARCHAR, negated VARCHAR)"
    )
    con.executemany(
        "INSERT INTO edges VALUES (?, ?, 'biolink:DiseaseToPhenotypicFeatureAssociation', 'biolink:has_phenotype', NULL)",
        assoc_rows,
    )
    entities = sorted({e for e, _ in assoc_rows})
    con.execute("CREATE TABLE nodes(id VARCHAR, name VARCHAR)")
    con.executemany(
        "INSERT INTO nodes VALUES (?, ?)",
        [("A1", "a1"), ("B1", "b1"), ("A", "a"), ("B", "b"), ("R", "root")] + [(e, e) for e in entities],
    )
    con.execute("""CREATE TABLE information_content AS
        WITH clo AS (SELECT object_id AS o FROM closure WHERE predicate_id = 'rdfs:subClassOf'),
             n AS (SELECT count(DISTINCT o) AS nn FROM clo)
        SELECT o AS term, -log2(count(DISTINCT s)::DOUBLE / (SELECT nn FROM n)) AS ic
        FROM (SELECT subject_id AS s, object_id AS o FROM closure WHERE predicate_id='rdfs:subClassOf') GROUP BY o""")
    con.execute("""CREATE TABLE closure_size AS
        SELECT e.subject AS entity, count(DISTINCT c.object_id) AS size
        FROM edges e JOIN closure c ON c.subject_id = e.object GROUP BY e.subject""")
    con.close()
    return Ducksim.from_duckdb(str(path))


@pytest.mark.parametrize("metric", METRICS)
def test_search_scores_finite_with_duplicate_associations(tmp_path, metric):
    """A duplicate (entity, phenotype) association must not produce inf/nan scores (or crash) — the
    intersection can't exceed the union, so the jaccard denominator stays positive."""
    eng = baked_kg(tmp_path / "dup.duckdb", DUP_ASSOC)
    scores = [s for _, s in eng.hybrid_search(["A1"], prefix="MONDO", metric=metric)]
    assert scores
    assert all(math.isfinite(s) for s in scores), (metric, scores)


def test_duplicate_association_is_idempotent(tmp_path):
    """Annotating an entity to the same phenotype twice must not change any score vs. once — the
    association set is a set, not a multiset (metamorphic guard for the count(*) intersection)."""
    uniq = baked_kg(tmp_path / "uniq.duckdb", UNIQ_ASSOC)
    dup = baked_kg(tmp_path / "dup.duckdb", DUP_ASSOC)
    for metric in METRICS:
        u = dict(uniq.hybrid_search(["A1"], prefix="MONDO", metric=metric))
        d = dict(dup.hybrid_search(["A1"], prefix="MONDO", metric=metric))
        assert u.keys() == d.keys(), metric
        for k in u:
            assert u[k] == pytest.approx(d[k]), (metric, k, u[k], d[k])


@pytest.mark.parametrize("metric", METRICS)
def test_search_score_bounds(tmp_path, metric):
    """Every score is finite and non-negative; jaccard additionally lies in [0, 1]."""
    eng = baked_kg(tmp_path / "kg.duckdb", DUP_ASSOC)
    for e, s in eng.hybrid_search(["A1"], prefix="MONDO", metric=metric):
        assert math.isfinite(s) and s >= 0.0, (metric, e, s)
        if metric == "jaccard_similarity":
            assert s <= 1.0 + 1e-9, (e, s)


def test_self_similarity_is_perfect_jaccard(tmp_path):
    """A term compared to itself is a perfect jaccard match (invariant independent of the dup bug)."""
    eng = baked_kg(tmp_path / "kg.duckdb", UNIQ_ASSOC)
    r = eng.termset_pairwise_similarity(["A1"], ["A1"], metric="jaccard_similarity")
    assert r["average_score"] == pytest.approx(1.0)
