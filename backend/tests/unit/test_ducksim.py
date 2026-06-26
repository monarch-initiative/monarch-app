"""Unit tests for the DuckDB similarity engine + DucksimService, on a tiny synthetic monarch-kg.

Ontology (reflexive subClassOf): A1 < A < R, B1 < B < R.  IC(A1) = -log2(1/5) = log2(5).
Entities (has_phenotype): E:1->A1, E:2->B1, E:3->{A1,B1}.
"""
import math

import duckdb
import pytest

from monarch_py.service.ducksim import Ducksim
from monarch_py.service.ducksim_service import DucksimService


def _mini_kg(tmp_path):
    p = tmp_path / "mini.duckdb"
    con = duckdb.connect(str(p))
    con.execute("CREATE TABLE closure(subject_id VARCHAR, predicate_id VARCHAR, object_id VARCHAR)")
    con.executemany("INSERT INTO closure VALUES (?, 'rdfs:subClassOf', ?)",
                    [("R", "R"), ("A", "A"), ("A", "R"), ("B", "B"), ("B", "R"),
                     ("A1", "A1"), ("A1", "A"), ("A1", "R"), ("B1", "B1"), ("B1", "B"), ("B1", "R")])
    con.execute("CREATE TABLE edges(subject VARCHAR, object VARCHAR, category VARCHAR, "
                "predicate VARCHAR, negated VARCHAR)")
    con.executemany("INSERT INTO edges VALUES (?, ?, "
                    "'biolink:DiseaseToPhenotypicFeatureAssociation', 'biolink:has_phenotype', NULL)",
                    [("E:1", "A1"), ("E:2", "B1"), ("E:3", "A1"), ("E:3", "B1")])
    con.execute("CREATE TABLE nodes(id VARCHAR, name VARCHAR)")
    con.executemany("INSERT INTO nodes VALUES (?, ?)",
                    [("A1", "a one"), ("B1", "b one"), ("A", "a"), ("B", "b"), ("R", "root")])
    con.close()
    return str(p)


def _bake(path):
    """Add the precompute tables koza's semsim-prep bakes into monarch-kg.duckdb, so the engine
    reads them instead of building at startup. SQL mirrors tools/bake_ducksim.py."""
    con = duckdb.connect(path)
    con.execute("""CREATE TABLE semsim_ic AS
        WITH clo AS (SELECT object_id AS o FROM closure WHERE predicate_id = 'rdfs:subClassOf'),
             n AS (SELECT count(DISTINCT o) AS nn FROM clo)
        SELECT o AS term, -log2(count(*)::DOUBLE / (SELECT nn FROM n)) AS ic FROM clo GROUP BY o""")
    con.execute("""CREATE TABLE semsim_closure_size AS
        SELECT e.subject AS entity, count(DISTINCT c.object_id) AS size
        FROM edges e JOIN closure c ON c.subject_id = e.object GROUP BY e.subject""")
    con.close()
    return path


@pytest.fixture
def engine(tmp_path):
    return Ducksim.from_duckdb(_mini_kg(tmp_path))


def test_baked_tables_used(tmp_path):
    """The production path: engine reads pre-baked semsim_ic / semsim_closure_size and yields the
    same scores as the runtime-built path (locks the 'same closure ⇒ same IC' invariant)."""
    eng = Ducksim.from_duckdb(_bake(_mini_kg(tmp_path)))
    assert eng._baked("semsim_ic") and eng._baked("semsim_closure_size")
    # IC read from the baked table — identical to the built-path result
    assert eng.termset_pairwise_similarity(["A1"], ["A1"])["average_score"] == pytest.approx(math.log2(5))
    # search uses the baked closure-size table
    assert [e for e, _ in eng.hybrid_search(["A1"], limit=3, prefix="E")][:2] == ["E:1", "E:3"]


def test_compare_empty_objects_scores_zero(engine):
    """No object terms ⇒ no matches; scores floor at 0.0 (no -1.0 sentinel leak)."""
    r = engine.termset_pairwise_similarity(["A1"], [])
    assert r["average_score"] == pytest.approx(0.0)
    assert r["best_score"] == pytest.approx(0.0)
    assert all(bm["score"] >= 0.0 for bm in r["subject_best_matches"].values())


def test_self_compare_is_avg_ic(engine):
    r = engine.termset_pairwise_similarity(["A1"], ["A1"])
    assert r["average_score"] == pytest.approx(math.log2(5))  # best match of A1 is itself = IC(A1)


def test_service_compare_model(engine):
    svc = DucksimService(engine=engine, entity_implementation=None)
    tsps = svc.compare(["A1"], ["B1"])
    assert tsps.metric == "ancestor_information_content"
    bm = tsps.subject_best_matches["A1"]
    assert bm.match_target == "B1"
    assert bm.match_source_label == "a one"          # label pulled from nodes.name
    assert bm.match_subsumer == "R"                  # A1 & B1 share only the root
    assert bm.match_subsumer_label == "root"
    assert bm.score == pytest.approx(0.0)            # IC(root) = -log2(5/5) = 0
    assert tsps.model_dump_json()                    # serializes cleanly


def test_search_ranking(engine):
    # query A1 over prefix "E": E:1 (exact) > E:3 (half) > E:2 (root-only)
    ranked = engine.hybrid_search(["A1"], limit=3, prefix="E")
    assert [e for e, _ in ranked][:2] == ["E:1", "E:3"]


def test_directionality(engine):
    # E:3 phenotypes {A1,B1}, query {A1}; the entity is the subject.
    #   subject_to_object (entity->query): (IC(A1) + 0) / 2 = IC(A1)/2
    #   object_to_subject (query->entity): IC(A1) / 1     = IC(A1)
    s2o = dict(engine.full_search(["A1"], prefix="E", direction="subject_to_object"))
    o2s = dict(engine.full_search(["A1"], prefix="E", direction="object_to_subject"))
    assert s2o["E:3"] == pytest.approx(math.log2(5) / 2)
    assert o2s["E:3"] == pytest.approx(math.log2(5))


def test_termset_direction_matches_search(engine):
    """compare's average_score honors `direction` and equals the directional search ranking for the
    same entity (E:3 phenotypes {A1,B1} as subjects, query {A1} as objects — the search orientation)."""
    s2o = engine.termset_pairwise_similarity(["A1", "B1"], ["A1"], direction="subject_to_object")
    o2s = engine.termset_pairwise_similarity(["A1", "B1"], ["A1"], direction="object_to_subject")
    assert s2o["average_score"] == pytest.approx(math.log2(5) / 2)
    assert o2s["average_score"] == pytest.approx(math.log2(5))
    assert s2o["average_score"] == pytest.approx(
        dict(engine.full_search(["A1"], prefix="E", direction="subject_to_object"))["E:3"])
    assert o2s["average_score"] == pytest.approx(
        dict(engine.full_search(["A1"], prefix="E", direction="object_to_subject"))["E:3"])
