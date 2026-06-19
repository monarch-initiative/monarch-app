"""Unit tests for the /pathograph FastAPI route.

Exercises the artifact loader, the disease pass-through, and the gene
anchor-merge against a crafted local artifact directory (no network).
"""

import json

import pytest
from fastapi.testclient import TestClient

from monarch_py.api import pathograph as route
from monarch_py.api.main import app

# Two disorders that share a gene (hgnc:111) and a phenotype (HP:0001250), and
# each have a free-text mechanism node with the SAME label (must NOT merge).
DISORDER_A = {
    "nodes": [
        {"id": "GeneX", "node_type": "genetic", "meta": {"gene_terms": [{"label": "GeneX", "id": "hgnc:111"}]}},
        {"id": "Mechanism", "node_type": "pathophysiology", "description": "A's mechanism"},
        {"id": "Seizure", "node_type": "phenotype", "meta": {"term_id": "HP:0001250"}},
    ],
    "edges": [
        {"source": "GeneX", "target": "Mechanism", "predicate": "causes"},
        {"source": "Mechanism", "target": "Seizure", "predicate": "causes"},
    ],
    "orphan_targets": [],
}
DISORDER_B = {
    "nodes": [
        {"id": "GeneX", "node_type": "genetic", "meta": {"gene_terms": [{"label": "GeneX", "id": "hgnc:111"}]}},
        {"id": "Mechanism", "node_type": "pathophysiology", "description": "B's mechanism"},
        {"id": "Seizure", "node_type": "phenotype", "meta": {"term_id": "HP:0001250"}},
    ],
    "edges": [
        {"source": "GeneX", "target": "Mechanism", "predicate": "causes"},
        {"source": "Mechanism", "target": "Seizure", "predicate": "causes"},
    ],
    "orphan_targets": [],
}


@pytest.fixture
def artifact_dir(tmp_path, monkeypatch):
    (tmp_path / "MONDO_0000001.json").write_text(json.dumps(DISORDER_A))
    (tmp_path / "MONDO_0000002.json").write_text(json.dumps(DISORDER_B))
    (tmp_path / "index.json").write_text(
        json.dumps(
            {
                "MONDO:0000001": [{"file": "MONDO_0000001.json", "name": "Disease A", "slug": "Disease_A"}],
                "MONDO:0000002": [{"file": "MONDO_0000002.json", "name": "Disease B", "slug": "Disease_B"}],
            }
        )
    )
    (tmp_path / "by_gene.json").write_text(json.dumps({"hgnc:111": ["MONDO:0000001", "MONDO:0000002"]}))
    monkeypatch.setattr(route.settings, "dismech_pathographs_url", str(tmp_path))
    return tmp_path


@pytest.fixture(autouse=True)
def clear_cache():
    route._index_cache.clear()
    yield
    route._index_cache.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_disease_returns_passthrough_graph(client, artifact_dir):
    r = client.get("/v3/api/pathograph/MONDO:0000001")
    assert r.status_code == 200
    body = r.json()
    assert body["category"] == "disease"
    assert body["node_id"] == "MONDO:0000001"
    assert [s["id"] for s in body["sources"]] == ["MONDO:0000001"]
    # Source deep-links to the disorder's dismech page, built from its slug.
    assert body["sources"][0]["url"].endswith("/pages/disorders/Disease_A.html")
    assert len(body["nodes"]) == 3
    assert len(body["edges"]) == 2
    # The free-text mechanism node is namespaced by its Mondo id.
    ids = {n["id"] for n in body["nodes"]}
    assert "MONDO:0000001::Mechanism" in ids
    assert "HP:0001250" in ids  # phenotype anchored on its HP id
    assert "GENE:hgnc:111" in ids  # gene anchored on its HGNC id


def test_gene_merges_and_boxes_shared_nodes(client, artifact_dir):
    r = client.get("/v3/api/pathograph/HGNC:111")
    assert r.status_code == 200
    body = r.json()
    assert body["category"] == "gene"
    assert {s["id"] for s in body["sources"]} == {"MONDO:0000001", "MONDO:0000002"}

    nodes = {n["id"]: n for n in body["nodes"]}
    # Shared gene and phenotype collapse to one node carrying both disorders.
    assert sorted(nodes["GENE:hgnc:111"]["sources"]) == ["MONDO:0000001", "MONDO:0000002"]
    assert sorted(nodes["HP:0001250"]["sources"]) == ["MONDO:0000001", "MONDO:0000002"]
    # Same-named free-text mechanisms stay separate (one lane per disorder).
    assert "MONDO:0000001::Mechanism" in nodes
    assert "MONDO:0000002::Mechanism" in nodes
    # gene + phenotype (1 each) + 2 local mechanisms = 4 nodes
    assert len(body["nodes"]) == 4
    # GeneX->MechA, GeneX->MechB, MechA->HP, MechB->HP = 4 edges
    assert len(body["edges"]) == 4


def test_unknown_ids_return_404(client, artifact_dir):
    assert client.get("/v3/api/pathograph/MONDO:0009999").status_code == 404
    assert client.get("/v3/api/pathograph/HGNC:9999999").status_code == 404
    # Not a disease or gene.
    assert client.get("/v3/api/pathograph/CHEBI:12345").status_code == 404


def test_malformed_curie_returns_400(client, artifact_dir):
    r = client.get("/v3/api/pathograph/FOO:bar-baz")
    assert r.status_code == 400
