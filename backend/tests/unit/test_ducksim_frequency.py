"""The frequency tie-break and per-match frequencies in ducksim search, on a tiny synthetic KG.

Ontology: A1 < A < R, A2 < A. Four diseases annotated to A1 alone, with different recorded frequencies:
MONDO:1 9 of 10 patients (0.9), MONDO:2 "Occasional" (HPO category, 0.17), MONDO:3 none recorded,
MONDO:4 0 of 5 patients (0, floored to 0.01 by the tie-break). A query for A1 scores all four the
same, so only the tie-break separates them.
"""

import duckdb
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from monarch_py.api import semsim as semsim_module
from monarch_py.api.semsim import router
from monarch_py.service.ducksim import Ducksim
from monarch_py.service.ducksim_service import DucksimService

D2P = "biolink:DiseaseToPhenotypicFeatureAssociation"
EDGES = [
    ("MONDO:1", "A1", "0.9", None),
    ("MONDO:2", "A1", None, "HP:0040283"),
    ("MONDO:3", "A1", None, None),
    ("MONDO:4", "A1", "0.0", None),
]


@pytest.fixture
def engine(tmp_path):
    return _engine(tmp_path, EDGES)


def _engine(tmp_path, edges):
    path = str(tmp_path / "kg.duckdb")
    con = duckdb.connect(path)
    con.execute("CREATE TABLE closure(subject_id VARCHAR, predicate_id VARCHAR, object_id VARCHAR)")
    con.executemany(
        "INSERT INTO closure VALUES (?, 'rdfs:subClassOf', ?)",
        [
            ("R", "R"),
            ("A", "A"),
            ("A", "R"),
            ("A1", "A1"),
            ("A1", "A"),
            ("A1", "R"),
            ("A2", "A2"),
            ("A2", "A"),
            ("A2", "R"),
        ],
    )
    con.execute(
        """CREATE TABLE edges(subject VARCHAR, object VARCHAR, category VARCHAR, predicate VARCHAR,
        negated VARCHAR, has_quotient VARCHAR, frequency_qualifier VARCHAR)"""
    )
    con.executemany(
        f"INSERT INTO edges VALUES (?, ?, '{D2P}', 'biolink:has_phenotype', NULL, ?, ?)",
        edges,
    )
    con.execute("CREATE TABLE nodes(id VARCHAR, name VARCHAR, category VARCHAR)")
    con.executemany("INSERT INTO nodes VALUES (?, ?, 'biolink:Disease')", sorted({(e, e) for e, *_ in edges}))
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
    con.close()
    return Ducksim.from_duckdb(path)


def _order(results):
    return [e for e, *_ in results]


def test_recorded_frequencies(engine):
    freq = engine.frequencies_batch(["MONDO:1", "MONDO:2", "MONDO:3", "MONDO:4"])
    assert freq == {
        ("MONDO:1", "A1"): pytest.approx(0.9),
        ("MONDO:2", "A1"): pytest.approx(0.17),
        ("MONDO:4", "A1"): 0.0,  # 0 of 5 patients, reported as recorded
    }


@pytest.mark.parametrize("mode", ["hybrid", "full"])
def test_without_a_tie_break_ties_stay_in_id_order(engine, mode):
    assert _order(engine.search(["A1"], prefix="MONDO", mode=mode)) == ["MONDO:1", "MONDO:2", "MONDO:3", "MONDO:4"]


@pytest.mark.parametrize("mode", ["hybrid", "full"])
def test_frequency_tie_break_orders_ties_by_frequency(engine, mode):
    """Missing frequencies take the default, 0.5, which ranks above a recorded "occasional"."""
    results = engine.search(["A1"], prefix="MONDO", mode=mode, tie_break="frequency")
    assert _order(results) == ["MONDO:1", "MONDO:3", "MONDO:2", "MONDO:4"]
    assert len({round(s, 9) for _, s, _ in results}) == 1  # the scores themselves don't change


def test_default_frequency_moves_entities_without_one(engine):
    results = engine.full_search(["A1"], prefix="MONDO", tie_break="frequency", default_frequency=0.1)
    assert _order(results) == ["MONDO:1", "MONDO:2", "MONDO:3", "MONDO:4"]


def test_tie_break_applies_before_the_limit(engine):
    """The limit keeps the best of the tie group by frequency, not the first ids."""
    assert _order(engine.full_search(["A1"], prefix="MONDO", tie_break="frequency", limit=2)) == ["MONDO:1", "MONDO:3"]


def test_best_matches_carry_the_recorded_frequency(engine):
    by_entity = {e: c for e, _, c in engine.search(["A1"], prefix="MONDO", mode="full")}
    assert by_entity["MONDO:1"]["object_best_matches"]["A1"]["frequency"] == pytest.approx(0.9)
    assert by_entity["MONDO:1"]["subject_best_matches"]["A1"]["frequency"] == pytest.approx(0.9)
    assert by_entity["MONDO:3"]["object_best_matches"]["A1"]["frequency"] is None


def test_an_exact_annotation_uses_its_own_frequency(tmp_path):
    """Under Resnik, A1 matches a query for A as well as A itself does. MONDO:10 records A as
    occasional and A1 in 9 of 10 patients; the tie-break must use A's 0.17, not A1's 0.9, so MONDO:11
    (A, no frequency recorded, so the default 0.5) ranks first."""
    eng = _engine(
        tmp_path,
        [("MONDO:10", "A", None, "HP:0040283"), ("MONDO:10", "A1", "0.9", None), ("MONDO:11", "A", None, None)],
    )
    for direction in ("object_to_subject", "bidirectional"):
        results = eng.search(["A"], prefix="MONDO", mode="full", direction=direction, tie_break="frequency")
        assert _order(results) == ["MONDO:11", "MONDO:10"], direction
        match = dict((e, c) for e, _, c in results)["MONDO:10"]["object_best_matches"]["A"]
        assert match["match_target"] == "A"
        assert match["frequency"] == pytest.approx(0.17)


def test_the_reported_match_is_the_one_the_tie_break_used(tmp_path):
    """MONDO:20 has no annotation of the query term A, only its children A1 and A2, which match it
    equally. The tie-break and the reported match both take A1, the lower id."""
    eng = _engine(
        tmp_path,
        [
            ("MONDO:20", "A1", "0.1", None),
            ("MONDO:20", "A2", "0.9", None),
            ("MONDO:21", "A1", None, None),
            ("MONDO:21", "A2", None, None),
        ],
    )
    results = eng.search(["A"], prefix="MONDO", mode="full", direction="object_to_subject", tie_break="frequency")
    assert _order(results) == ["MONDO:21", "MONDO:20"]  # 0.5 (default) beats A1's 0.1
    match = dict((e, c) for e, _, c in results)["MONDO:20"]["object_best_matches"]["A"]
    assert (match["match_target"], match["frequency"]) == ("A1", pytest.approx(0.1))


def test_kg_without_frequency_columns_ties_fall_back_to_id_order(tmp_path):
    from tests.unit.test_ducksim import _bake, _mini_kg  # edges there have no frequency columns

    eng = Ducksim.from_duckdb(_bake(_mini_kg(tmp_path)))
    plain = eng.full_search(["A1"], prefix="E")
    assert eng.full_search(["A1"], prefix="E", tie_break="frequency") == plain


def test_unknown_tie_break_is_rejected(engine):
    with pytest.raises(ValueError, match="tie_break"):
        engine.full_search(["A1"], prefix="MONDO", tie_break="random")


def test_api_frequency_tie_break(engine, monkeypatch):
    service = DucksimService(engine=engine)
    monkeypatch.setattr(semsim_module, "semsim_service", lambda engine=None: service)
    monkeypatch.setattr(semsim_module, "resolve_engine", lambda engine=None: "ducksim")
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    response = client.get("/search/A1/Human Diseases?tie_break=frequency&default_frequency=0.1")
    assert response.status_code == status.HTTP_200_OK, response.text
    body = response.json()
    assert [r["subject"]["id"] for r in body] == ["MONDO:1", "MONDO:2", "MONDO:3", "MONDO:4"]
    assert body[0]["search_settings"]["tie_break"] == "frequency"
    assert body[0]["search_settings"]["default_frequency"] == pytest.approx(0.1)
    assert body[0]["similarity"]["object_best_matches"]["A1"]["frequency"] == pytest.approx(0.9)
    assert client.get("/search/A1/Human Diseases?default_frequency=2").status_code == 422


def test_api_default_frequency_alone_keeps_the_engine(engine, monkeypatch):
    """default_frequency does nothing without the frequency tie-break, so it must not switch a
    request to ducksim."""
    service = DucksimService(engine=engine)
    calls = []

    def fake_service(name=None):
        calls.append(name)
        return service

    monkeypatch.setattr(semsim_module, "semsim_service", fake_service)
    monkeypatch.setattr(semsim_module, "resolve_engine", lambda engine=None: "semsimian")
    app = FastAPI()
    app.include_router(router)
    response = TestClient(app).get("/search/A1/Human Diseases?default_frequency=0.3")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert calls == ["semsimian"]
    settings = response.json()[0]["search_settings"]
    assert settings["engine"] == "semsimian"
    assert settings["default_frequency"] == pytest.approx(0.5)
