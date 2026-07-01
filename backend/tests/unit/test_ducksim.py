"""Unit tests for the DuckDB similarity engine + DucksimService, on a tiny synthetic monarch-kg.

Ontology (reflexive subClassOf): A1 < A < R, B1 < B < R.  IC(A1) = -log2(1/5) = log2(5).
Entities (has_phenotype): E:1->A1, E:2->B1, E:3->{A1,B1}.  E:4->A1 but negated (excluded).
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
    con.executemany(
        "INSERT INTO closure VALUES (?, 'rdfs:subClassOf', ?)",
        [
            ("R", "R"),
            ("A", "A"),
            ("A", "R"),
            ("B", "B"),
            ("B", "R"),
            ("A1", "A1"),
            ("A1", "A"),
            ("A1", "R"),
            ("B1", "B1"),
            ("B1", "B"),
            ("B1", "R"),
        ],
    )
    con.execute(
        "CREATE TABLE edges(subject VARCHAR, object VARCHAR, category VARCHAR, predicate VARCHAR, negated VARCHAR)"
    )
    con.executemany(
        "INSERT INTO edges VALUES (?, ?, 'biolink:DiseaseToPhenotypicFeatureAssociation', 'biolink:has_phenotype', ?)",
        [("E:1", "A1", None), ("E:2", "B1", None), ("E:3", "A1", None), ("E:3", "B1", None), ("E:4", "A1", "True")],
    )  # negated assoc (VARCHAR 'True') — must be excluded
    con.execute("CREATE TABLE nodes(id VARCHAR, name VARCHAR)")
    con.executemany(
        "INSERT INTO nodes VALUES (?, ?)", [("A1", "a one"), ("B1", "b one"), ("A", "a"), ("B", "b"), ("R", "root")]
    )
    con.close()
    return str(p)


def _bake(path):
    """Add the precompute tables koza's information-content op bakes into monarch-kg.duckdb, so the
    engine reads them instead of building at startup. Table names MUST match what the engine's
    _baked() checks (information_content / closure_size); SQL mirrors koza's information-content
    operation (and the engine's own runtime-build fallback)."""
    con = duckdb.connect(path)
    con.execute("""CREATE TABLE information_content AS
        WITH clo AS (SELECT object_id AS o FROM closure WHERE predicate_id = 'rdfs:subClassOf'),
             n AS (SELECT count(DISTINCT o) AS nn FROM clo)
        SELECT o AS term, -log2(count(*)::DOUBLE / (SELECT nn FROM n)) AS ic FROM clo GROUP BY o""")
    con.execute("""CREATE TABLE closure_size AS
        SELECT e.subject AS entity, count(DISTINCT c.object_id) AS size
        FROM edges e JOIN closure c ON c.subject_id = e.object GROUP BY e.subject""")
    con.close()
    return path


@pytest.fixture
def engine(tmp_path):
    # ducksim reads koza's precompute tables; bake them like the KG build does (see _bake).
    return Ducksim.from_duckdb(_bake(_mini_kg(tmp_path)))


def test_reads_baked_precompute_tables(tmp_path):
    """ducksim is a pure reader of koza's information_content / closure_size tables: IC scores come
    from the baked table and search uses the baked closure sizes."""
    eng = Ducksim.from_duckdb(_bake(_mini_kg(tmp_path)))
    assert eng._baked("information_content") and eng._baked("closure_size")
    # IC(A1) = -log2(1/5); read straight from the baked information_content table
    assert eng.termset_pairwise_similarity(["A1"], ["A1"])["average_score"] == pytest.approx(math.log2(5))
    assert [e for e, _ in eng.hybrid_search(["A1"], limit=3, prefix="E")][:2] == ["E:1", "E:3"]


def test_missing_precompute_tables_fail_loud(tmp_path):
    """A db without koza's precompute tables is rejected (no silent recompute that could diverge)."""
    with pytest.raises(RuntimeError, match="information_content"):
        Ducksim.from_duckdb(_mini_kg(tmp_path))  # _mini_kg has closure/edges/nodes but no precomputes


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
    assert bm.match_source_label == "a one"  # label pulled from nodes.name
    assert bm.match_subsumer == "R"  # A1 & B1 share only the root
    assert bm.match_subsumer_label == "root"
    assert bm.score == pytest.approx(0.0)  # IC(root) = -log2(5/5) = 0
    assert tsps.model_dump_json()  # serializes cleanly


def test_search_ranking(engine):
    # query A1 over prefix "E": E:1 (exact) > E:3 (half) > E:2 (root-only)
    ranked = engine.hybrid_search(["A1"], limit=3, prefix="E")
    assert [e for e, _ in ranked][:2] == ["E:1", "E:3"]


def test_duplicate_associations_dont_inflate_jaccard(tmp_path):
    """An entity annotated to the same phenotype via multiple association rows (different evidence)
    must not double-count that phenotype's ancestors: the count(*) intersection would exceed the
    union, giving a zero/negative jaccard denominator — an inf score (JSON-unserializable -> API 500)
    and sqrt-of-negative for phenodigm. Regression for the MGI/ZFIN cross-species search 500s."""
    path = _mini_kg(tmp_path)
    con = duckdb.connect(path)
    # E:1 already has has_phenotype A1; add a duplicate association row for the same (E:1, A1).
    con.execute(
        "INSERT INTO edges VALUES ('E:1', 'A1', "
        "'biolink:DiseaseToPhenotypicFeatureAssociation', 'biolink:has_phenotype', NULL)"
    )
    con.close()
    eng = Ducksim.from_duckdb(_bake(path))
    for metric in ("jaccard_similarity", "phenodigm_score"):
        scores = [s for _, s in eng.hybrid_search(["A1"], prefix="E", metric=metric)]
        assert scores, metric
        assert all(math.isfinite(s) for s in scores), (metric, scores)
    # de-duped, E:1 (phenotype {A1}) vs query {A1} is still a perfect jaccard match
    assert dict(eng.hybrid_search(["A1"], prefix="E", metric="jaccard_similarity"))["E:1"] == pytest.approx(1.0)


def test_directionality(engine):
    # E:3 phenotypes {A1,B1}, query {A1}; the entity is the subject.
    #   subject_to_object (entity->query): (IC(A1) + 0) / 2 = IC(A1)/2
    #   object_to_subject (query->entity): IC(A1) / 1     = IC(A1)
    s2o = dict(engine.full_search(["A1"], prefix="E", direction="subject_to_object"))
    o2s = dict(engine.full_search(["A1"], prefix="E", direction="object_to_subject"))
    assert s2o["E:3"] == pytest.approx(math.log2(5) / 2)
    assert o2s["E:3"] == pytest.approx(math.log2(5))


def test_negated_associations_excluded(engine):
    """A negated has_phenotype edge never enters the association set, so its entity has no phenotypes
    and is unsearchable. Locks the `negated` filter (try_cast to BOOLEAN — robust to casing / a future
    boolean column), which the rest of the fixture (all-NULL negated) otherwise never exercises."""
    assert engine.entity_phenotypes_batch(["E:4"]) == {}  # only edge is negated -> no phenotypes
    assert "E:4" not in [e for e, _ in engine.hybrid_search(["A1"], limit=10, prefix="E")]
    # the non-negated entities are unaffected
    assert engine.entity_phenotypes_batch(["E:1"]) == {"E:1": ["A1"]}


def test_search_hydrates_from_duckdb_without_entity_store(engine):
    """All-DuckDB search: the service builds full SemsimSearchResults — including the result entity,
    hydrated from the KG `nodes` table — with no external entity store (entity_implementation=None)."""
    svc = DucksimService(engine=engine)  # no entity_implementation passed
    results = svc.search(["A1"], "E", limit=3)
    assert [r.subject.id for r in results][:2] == ["E:1", "E:3"]
    top = results[0]
    assert top.subject.name == "a one" or top.subject.id == "E:1"  # subject hydrated from nodes
    assert top.similarity.metric == "ancestor_information_content"
    assert top.score == pytest.approx(top.similarity.average_score)  # ranking == enriched score
    assert top.similarity.model_dump_json()  # serializes cleanly


def test_batched_search_matches_per_entity_path(engine):
    """The batched engine.search payload equals the old per-entity path (hybrid_search +
    per-entity termset_pairwise_similarity) — the refactor changed how, not what, is computed."""
    termset, prefix = ["A1", "B1"], "E"
    new = engine.search(termset, limit=5, prefix=prefix)
    # readable reference: rank, then score each entity on its own (one termset_pairwise_similarity
    # per entity) instead of the batched single-query path engine.search uses.
    phenos = engine.entity_phenotypes_batch([e for e, _ in engine.hybrid_search(termset, limit=5, prefix=prefix)])
    ref = [
        (e, s, engine.termset_pairwise_similarity(sorted(phenos.get(e, [])), termset))
        for e, s in engine.hybrid_search(termset, limit=5, prefix=prefix)
    ]
    assert [e for e, _, _ in new] == [e for e, _, _ in ref]  # same ranking
    for (_, ns, nc), (_, rs, rc) in zip(new, ref):
        assert ns == pytest.approx(rs)
        assert nc["average_score"] == pytest.approx(rc["average_score"])
        assert nc["best_score"] == pytest.approx(rc["best_score"])
        assert nc["subject_best_matches"].keys() == rc["subject_best_matches"].keys()
        for k, bm in nc["subject_best_matches"].items():
            assert bm["match_target"] == rc["subject_best_matches"][k]["match_target"]
            assert bm["score"] == pytest.approx(rc["subject_best_matches"][k]["score"])


def test_termset_direction_matches_search(engine):
    """compare's average_score honors `direction` and equals the directional search ranking for the
    same entity (E:3 phenotypes {A1,B1} as subjects, query {A1} as objects — the search orientation)."""
    s2o = engine.termset_pairwise_similarity(["A1", "B1"], ["A1"], direction="subject_to_object")
    o2s = engine.termset_pairwise_similarity(["A1", "B1"], ["A1"], direction="object_to_subject")
    assert s2o["average_score"] == pytest.approx(math.log2(5) / 2)
    assert o2s["average_score"] == pytest.approx(math.log2(5))
    assert s2o["average_score"] == pytest.approx(
        dict(engine.full_search(["A1"], prefix="E", direction="subject_to_object"))["E:3"]
    )
    assert o2s["average_score"] == pytest.approx(
        dict(engine.full_search(["A1"], prefix="E", direction="object_to_subject"))["E:3"]
    )
