"""API-contract tests for the ducksim search endpoint.

Drives the real FastAPI semsim router with a ducksim backend over a tiny baked KG and asserts every
metric x directionality returns 200 with a JSON-serializable body. This is the boundary where an
inf/nan score turns into a 500 (starlette's json.dumps uses allow_nan=False), so it catches the class
of failure the engine-only tests can miss.
"""

import duckdb
import pytest
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

from monarch_py.api import semsim as semsim_module
from monarch_py.api.semsim import router
from monarch_py.service.ducksim import Ducksim
from monarch_py.service.ducksim_service import DucksimService

METRICS = ["ancestor_information_content", "jaccard_similarity", "phenodigm_score"]
DIRECTIONS = ["bidirectional", "subject_to_object", "object_to_subject"]

# MONDO:1 annotated to A1 twice — a duplicate association, to exercise the serialization boundary.
ASSOC = [("MONDO:1", "A1"), ("MONDO:1", "A1"), ("MONDO:2", "B1"), ("MONDO:3", "A1")]


def _baked_kg(path, assoc_rows):
    con = duckdb.connect(str(path))
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
        "INSERT INTO edges VALUES (?, ?, 'biolink:DiseaseToPhenotypicFeatureAssociation', 'biolink:has_phenotype', NULL)",
        assoc_rows,
    )
    entities = sorted({e for e, _ in assoc_rows})
    con.execute("CREATE TABLE nodes(id VARCHAR, name VARCHAR, category VARCHAR)")
    con.executemany(
        "INSERT INTO nodes VALUES (?, ?, 'biolink:Disease')",
        [(e, e) for e in entities] + [("A1", "a1"), ("B1", "b1")],
    )
    con.execute(
        """CREATE TABLE information_content AS
        WITH clo AS (SELECT subject_id AS s, object_id AS o FROM closure WHERE predicate_id='rdfs:subClassOf'),
             n AS (SELECT count(DISTINCT o) AS nn FROM clo)
        SELECT o AS term, -log2(count(DISTINCT s)::DOUBLE / (SELECT nn FROM n)) AS ic FROM clo GROUP BY o"""
    )
    con.execute(
        """CREATE TABLE closure_size AS
        SELECT e.subject AS entity, count(DISTINCT c.object_id) AS size
        FROM edges e JOIN closure c ON c.subject_id = e.object GROUP BY e.subject"""
    )
    con.close()
    return Ducksim.from_duckdb(str(path))


@pytest.fixture
def ducksim_client(tmp_path, monkeypatch):
    service = DucksimService(engine=_baked_kg(tmp_path / "kg.duckdb", ASSOC))
    # route every semsim_service() call in the router to our in-memory ducksim service
    monkeypatch.setattr(semsim_module, "semsim_service", lambda engine=None: service)
    monkeypatch.setattr(semsim_module, "resolve_engine", lambda engine=None: "ducksim")
    return TestClient(router)


@pytest.mark.parametrize("metric", METRICS)
@pytest.mark.parametrize("directionality", DIRECTIONS)
def test_post_search_serializes_all_metrics_and_directions(ducksim_client, metric, directionality):
    response = ducksim_client.post(
        "/search/",
        json={
            "termset": ["A1"],
            "group": "Human Diseases",
            "metric": metric,
            "directionality": directionality,
            "limit": 5,
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    body = response.json()  # raises / errors if an inf/nan score reached the response
    assert isinstance(body, list) and body


@pytest.mark.parametrize("metric", METRICS)
def test_get_search_serializes_all_metrics(ducksim_client, metric):
    response = ducksim_client.get(f"/search/A1/Human Diseases?metric={metric}&limit=5")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert isinstance(response.json(), list)


@pytest.mark.parametrize("search_mode", ["hybrid", "full"])
@pytest.mark.parametrize("directionality", DIRECTIONS)
def test_search_returns_direction_scores_and_settings(ducksim_client, search_mode, directionality):
    """Every result carries both direction averages and the settings the search ran with. The ranked
    score is the selected direction, or the mean of the two for bidirectional."""
    response = ducksim_client.get(
        f"/search/A1,B1/Human Diseases?limit=5&search_mode={search_mode}&directionality={directionality}"
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    body = response.json()
    assert body
    for result in body:
        s2o, o2s = result["subject_to_object_score"], result["object_to_subject_score"]
        expected = {"subject_to_object": s2o, "object_to_subject": o2s, "bidirectional": (s2o + o2s) / 2}
        assert result["score"] == pytest.approx(expected[directionality])
        assert result["search_settings"] == {
            "engine": "ducksim",
            "metric": "ancestor_information_content",
            "directionality": directionality,
            "search_mode": search_mode,
            "information_content": "ontology",
            "tie_break": "none",
            "default_frequency": 0.5,
        }


def test_post_search_accepts_search_mode(ducksim_client):
    response = ducksim_client.post(
        "/search/", json={"termset": ["A1"], "group": "Human Diseases", "search_mode": "full", "limit": 5}
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    assert all(r["search_settings"]["search_mode"] == "full" for r in response.json())


def test_unknown_search_mode_is_rejected(ducksim_client):
    # A bare router (no app exception handlers) raises the validation error the app turns into a 422.
    with pytest.raises(RequestValidationError, match="search_mode"):
        ducksim_client.get("/search/A1/Human Diseases?search_mode=exhaustive")


@pytest.fixture
def ducksim_app_client(ducksim_client):
    app = FastAPI()  # an app, not a bare router, so HTTPExceptions become responses
    app.include_router(router)
    return TestClient(app)


@pytest.mark.parametrize("directionality", DIRECTIONS)
def test_compare_average_follows_directionality(ducksim_app_client, directionality):
    """A1 vs {A1, B1}: A1's best match is itself, B1 shares only the root (IC 0). So
    subject_to_object = IC(A1), object_to_subject = IC(A1) / 2, bidirectional = their mean."""
    get = ducksim_app_client.get(f"/compare/A1/A1,B1?directionality={directionality}").json()
    post = ducksim_app_client.post(
        "/compare/", json={"subjects": ["A1"], "objects": ["A1", "B1"], "directionality": directionality}
    ).json()
    ic_a1 = get["subject_best_matches"]["A1"]["score"]
    expected = {"subject_to_object": ic_a1, "object_to_subject": ic_a1 / 2, "bidirectional": 0.75 * ic_a1}
    assert get["average_score"] == pytest.approx(expected[directionality])
    assert post["average_score"] == pytest.approx(expected[directionality])


def test_multicompare_scores_follow_directionality(ducksim_app_client):
    """Query A1 vs entity {A1, B1}. With search's convention, subject_to_object averages the
    entity's phenotypes (A1 -> IC(A1), B1 -> 0), so it is half of object_to_subject (the query's A1)."""
    body = {"subjects": ["A1"], "object_sets": [{"id": "X", "label": "x", "phenotypes": ["A1", "B1"]}]}
    bidirectional = ducksim_app_client.post("/multicompare/", json=body).json()[0]["score"]
    s2o = ducksim_app_client.post("/multicompare/", json={**body, "directionality": "subject_to_object"}).json()[0]
    o2s = ducksim_app_client.post("/multicompare/", json={**body, "directionality": "object_to_subject"}).json()[0]
    assert s2o["score"] == pytest.approx(bidirectional / 1.5)
    assert o2s["score"] == pytest.approx(bidirectional / 0.75)


@pytest.mark.parametrize("directionality", DIRECTIONS)
def test_multicompare_direction_means_what_it_does_in_search(ducksim_app_client, directionality):
    """The phenogrid pages send one direction to both search and multicompare, so an entity must get
    the same score, direction scores and settings from each."""
    search = ducksim_app_client.get(
        f"/search/A1,B1/Human Diseases?search_mode=full&directionality={directionality}&limit=10"
    ).json()
    from_search = {r["subject"]["id"]: r for r in search}["MONDO:1"]
    multi = ducksim_app_client.post(
        "/multicompare/",
        json={
            "subjects": ["A1", "B1"],
            "object_sets": [{"id": "MONDO:1", "label": "one", "phenotypes": ["A1"]}],
            "directionality": directionality,
        },
    ).json()[0]
    assert multi["score"] == pytest.approx(from_search["score"])
    assert multi["subject_to_object_score"] == pytest.approx(from_search["subject_to_object_score"])
    assert multi["object_to_subject_score"] == pytest.approx(from_search["object_to_subject_score"])
    assert multi["search_settings"]["engine"] == "ducksim"
    assert multi["search_settings"]["directionality"] == directionality
