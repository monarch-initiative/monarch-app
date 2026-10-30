"""Annotation-based information content in ducksim, on a tiny synthetic KG.

Ontology (reflexive subClassOf): A1 < A < R, B1 < B < R, C < R (C is never annotated).
Diseases (MONDO): M:1 -> A1, M:2 -> B1, M:3 -> {A1, B1}. Genes (HGNC): G:1 -> A1.

Annotation IC over the MONDO corpus (koza's annotation-information-content, N = 3 diseases):
IC(A1) = IC(A) = log2(3/2), IC(B1) = IC(B) = log2(3/2), IC(R) = 0, and C has no row.
Ontology IC, for contrast, gives every leaf the maximum: IC(A1) = -log2(1/6) = log2(6), over 6 terms.
"""

import math

import duckdb
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from monarch_py.api import semsim as semsim_module
from monarch_py.api.semsim import router
from monarch_py.service.ducksim import AnnotationICUnavailable, Ducksim
from monarch_py.service.ducksim_service import DucksimService

D2P = "biolink:DiseaseToPhenotypicFeatureAssociation"
G2P = "biolink:GeneToPhenotypicFeatureAssociation"
CLOSURE = [("R", "R"), ("A", "A"), ("A", "R"), ("B", "B"), ("B", "R"), ("C", "C"), ("C", "R")]
CLOSURE += [("A1", "A1"), ("A1", "A"), ("A1", "R"), ("B1", "B1"), ("B1", "B"), ("B1", "R")]
EDGES = [("MONDO:1", "A1", D2P), ("MONDO:2", "B1", D2P), ("MONDO:3", "A1", D2P), ("MONDO:3", "B1", D2P)]
EDGES += [("HGNC:1", "A1", G2P)]


def _kg(path, *, with_annotation_ic=True):
    con = duckdb.connect(str(path))
    con.execute("CREATE TABLE closure(subject_id VARCHAR, predicate_id VARCHAR, object_id VARCHAR)")
    con.executemany("INSERT INTO closure VALUES (?, 'rdfs:subClassOf', ?)", CLOSURE)
    con.execute(
        "CREATE TABLE edges(subject VARCHAR, object VARCHAR, category VARCHAR, predicate VARCHAR, negated VARCHAR)"
    )
    con.executemany("INSERT INTO edges VALUES (?, ?, ?, 'biolink:has_phenotype', NULL)", EDGES)
    con.execute("CREATE TABLE nodes(id VARCHAR, name VARCHAR, category VARCHAR)")
    con.executemany(
        "INSERT INTO nodes VALUES (?, ?, 'biolink:Disease')", [(e, e) for e in sorted({e for e, _, _ in EDGES})]
    )
    con.execute(
        """CREATE TABLE information_content AS
        WITH clo AS (SELECT object_id AS o FROM closure), n AS (SELECT count(DISTINCT o) AS nn FROM clo)
        SELECT o AS term, -log2(count(*)::DOUBLE / (SELECT nn FROM n)) AS ic FROM clo GROUP BY o"""
    )
    con.execute(
        """CREATE TABLE closure_size AS
        SELECT e.subject AS entity, count(DISTINCT c.object_id) AS size
        FROM edges e JOIN closure c ON c.subject_id = e.object GROUP BY e.subject"""
    )
    if with_annotation_ic:
        # the SQL koza's annotation-information-content runs, for the MONDO -> HP-style corpus
        con.execute(
            """CREATE TABLE annotation_information_content AS
            WITH a AS (SELECT DISTINCT subject AS entity, object AS term FROM edges WHERE subject LIKE 'MONDO:%'),
                 n AS (SELECT count(DISTINCT entity) AS nn FROM a)
            SELECT 'mondo_hp' AS corpus, c.object_id AS term, log2((SELECT nn FROM n)::DOUBLE / count(DISTINCT a.entity)) AS ic
            FROM a JOIN closure c ON c.subject_id = a.term GROUP BY c.object_id"""
        )
        con.execute(
            """CREATE TABLE pheno_comparison_corpora (corpus VARCHAR,
            subject_prefixes VARCHAR[], object_prefixes VARCHAR[])"""
        )
        con.execute("INSERT INTO pheno_comparison_corpora VALUES ('mondo_hp', ['MONDO'], ['HP'])")
        # a listed corpus with no IC rows (e.g. a build that skipped it) is not offered
        con.execute("INSERT INTO pheno_comparison_corpora VALUES ('rgd_mp', ['RGD'], ['MP'])")
    con.close()
    return Ducksim.from_duckdb(str(path))


@pytest.fixture
def engine(tmp_path):
    return _kg(tmp_path / "kg.duckdb")


def test_annotation_ic_views_are_keyed_by_subject_prefix(engine):
    assert engine.annotation_ic_views == {"MONDO": "_ic_annotation_mondo_hp"}
    assert engine.ic_view("ontology") == "_ic"
    assert engine.ic_view("annotation", "MONDO") == "_ic_annotation_mondo_hp"
    with pytest.raises(AnnotationICUnavailable, match="RGD"):
        engine.ic_view("annotation", "RGD")


def test_compare_uses_the_requested_ic(engine):
    ontology = engine.termset_pairwise_similarity(["A1"], ["A1"])
    annotation = engine.termset_pairwise_similarity(
        ["A1"], ["A1"], information_content="annotation", corpus_prefix="MONDO"
    )
    assert ontology["average_score"] == pytest.approx(math.log2(6))
    assert annotation["average_score"] == pytest.approx(math.log2(3 / 2))


def test_ancestor_without_annotation_ic_still_counts_toward_jaccard(engine):
    """C has no annotation-IC row. It must still count as a shared ancestor for Jaccard (with IC 0),
    or C-vs-C would score Jaccard 1/3 instead of 1."""
    r = engine.termset_pairwise_similarity(
        ["C"], ["C"], metric="jaccard_similarity", information_content="annotation", corpus_prefix="MONDO"
    )
    assert r["average_score"] == pytest.approx(1.0)
    pair = r["subject_best_matches"]["C"]["similarity"]
    assert pair["ancestor_information_content"] == pytest.approx(0.0)


@pytest.mark.parametrize("mode", ["hybrid", "full"])
def test_search_with_annotation_ic(engine, mode):
    results = engine.search(["A1"], prefix="MONDO", mode=mode, information_content="annotation", limit=5)
    scores = {e: s for e, s, _ in results}
    # MONDO:1 matches A1 exactly in both directions; with annotation IC that is worth log2(3/2)
    assert scores["MONDO:1"] == pytest.approx(math.log2(3 / 2))
    # the page detail reuses the same IC, so the comparison agrees with the ranked score
    assert all(c["average_score"] == pytest.approx(s) for _, s, c in results)


def test_ontology_ic_is_unchanged_by_the_left_join(engine):
    """Ontology IC has a row for every closure term, so switching the IC join to a left join can't
    change ontology-IC scores."""
    assert dict(engine.full_search(["A1"], prefix="MONDO"))["MONDO:1"] == pytest.approx(math.log2(6))


def test_annotation_ic_for_a_group_without_a_corpus_is_unavailable(engine):
    with pytest.raises(AnnotationICUnavailable, match="HGNC"):
        engine.search(["A1"], prefix="HGNC", information_content="annotation")
    with pytest.raises(AnnotationICUnavailable, match="group"):
        engine.termset_pairwise_similarity(["A1"], ["A1"], information_content="annotation")


def test_kg_without_annotation_ic_still_serves_ontology_ic(tmp_path):
    eng = _kg(tmp_path / "old.duckdb", with_annotation_ic=False)
    assert eng.annotation_ic_views == {}
    assert dict(eng.full_search(["A1"], prefix="MONDO"))["MONDO:1"] == pytest.approx(math.log2(6))
    with pytest.raises(AnnotationICUnavailable):
        eng.search(["A1"], prefix="MONDO", information_content="annotation")


# ---- API -------------------------------------------------------------------


@pytest.fixture
def client(engine, monkeypatch):
    service = DucksimService(engine=engine)
    monkeypatch.setattr(semsim_module, "semsim_service", lambda engine=None: service)
    monkeypatch.setattr(semsim_module, "resolve_engine", lambda engine=None: "ducksim")
    app = FastAPI()  # an app, not a bare router, so HTTPExceptions become responses
    app.include_router(router)
    return TestClient(app)


def test_api_search_with_annotation_ic(client):
    response = client.get("/search/A1/Human Diseases?information_content=annotation&search_mode=full")
    assert response.status_code == status.HTTP_200_OK, response.text
    body = response.json()
    assert body[0]["search_settings"]["information_content"] == "annotation"
    assert {r["subject"]["id"]: r["score"] for r in body}["MONDO:1"] == pytest.approx(math.log2(3 / 2))


def test_api_search_without_a_corpus_is_a_bad_request(client):
    response = client.get("/search/A1/Human Genes?information_content=annotation")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "HGNC" in response.json()["detail"]


def test_api_compare_with_annotation_ic(client):
    response = client.get("/compare/A1/A1?information_content=annotation&group=Human Diseases")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["average_score"] == pytest.approx(math.log2(3 / 2))
    response = client.post(
        "/compare/",
        json={"subjects": ["A1"], "objects": ["A1"], "information_content": "annotation", "group": "Human Diseases"},
    )
    assert response.json()["average_score"] == pytest.approx(math.log2(3 / 2))


def test_api_compare_with_annotation_ic_needs_a_group(client):
    response = client.get("/compare/A1/A1?information_content=annotation")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "group" in response.json()["detail"]


def test_api_multicompare_with_annotation_ic(client):
    response = client.post(
        "/multicompare/",
        json={
            "subjects": ["A1"],
            "object_sets": [{"id": "MONDO:1", "label": "one", "phenotypes": ["A1"]}],
            "information_content": "annotation",
            "group": "Human Diseases",
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()[0]["score"] == pytest.approx(math.log2(3 / 2))


def test_api_directionality_with_annotation_ic(client):
    """A1 vs {A1, B1} with annotation IC: A1 matches itself (log2(3/2)); B1 shares only the root (0)."""
    ic = math.log2(3 / 2)
    settings = "information_content=annotation&group=Human Diseases"
    s2o = client.get(f"/compare/A1/A1,B1?{settings}&directionality=subject_to_object").json()
    o2s = client.get(f"/compare/A1/A1,B1?{settings}&directionality=object_to_subject").json()
    assert (s2o["average_score"], o2s["average_score"]) == (pytest.approx(ic), pytest.approx(ic / 2))
    multi = client.post(
        "/multicompare/",
        json={
            "subjects": ["A1"],
            "object_sets": [{"id": "X", "label": "x", "phenotypes": ["A1", "B1"]}],
            "information_content": "annotation",
            "group": "Human Diseases",
            "directionality": "subject_to_object",
        },
    ).json()[0]
    assert multi["score"] == pytest.approx(ic / 2)  # the entity's phenotypes, as in search
    assert multi["search_settings"]["information_content"] == "annotation"
