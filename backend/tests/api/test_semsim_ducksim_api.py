"""API-contract tests for the ducksim search endpoint.

Drives the real FastAPI semsim router with a ducksim backend over a tiny baked KG and asserts every
metric x directionality returns 200 with a JSON-serializable body. This is the boundary where an
inf/nan score turns into a 500 (starlette's json.dumps uses allow_nan=False), so it catches the class
of failure the engine-only tests can miss.
"""

import duckdb
import pytest
from fastapi import status
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
    con.execute("CREATE TABLE nodes(id VARCHAR, name VARCHAR, category VARCHAR)")
    con.executemany(
        "INSERT INTO nodes VALUES (?, ?, 'biolink:Disease')",
        [(e, e) for e in entities] + [("A1", "a1"), ("B1", "b1")],
    )
    con.execute("""CREATE TABLE information_content AS
        WITH clo AS (SELECT subject_id AS s, object_id AS o FROM closure WHERE predicate_id='rdfs:subClassOf'),
             n AS (SELECT count(DISTINCT o) AS nn FROM clo)
        SELECT o AS term, -log2(count(DISTINCT s)::DOUBLE / (SELECT nn FROM n)) AS ic FROM clo GROUP BY o""")
    con.execute("""CREATE TABLE closure_size AS
        SELECT e.subject AS entity, count(DISTINCT c.object_id) AS size
        FROM edges e JOIN closure c ON c.subject_id = e.object GROUP BY e.subject""")
    con.close()
    return Ducksim.from_duckdb(str(path))


@pytest.fixture
def ducksim_client(tmp_path, monkeypatch):
    service = DucksimService(engine=_baked_kg(tmp_path / "kg.duckdb", ASSOC))
    # route every semsim_service() call in the router to our in-memory ducksim service
    monkeypatch.setattr(semsim_module, "semsim_service", lambda engine=None: service)
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
