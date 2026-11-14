"""DismechStore and the /dismech and /pathograph routes, against a tiny dismech.duckdb.

The fixture mirrors the tables monarch-ingest's `dismech-db` stage writes (core.* from a dismech
release, app.* sliced from the KG); only the columns the store reads are filled in.
"""

import json

import duckdb
import pytest
from fastapi.testclient import TestClient

from monarch_py.api import dismech as dismech_route
from monarch_py.api import pathograph as pathograph_route
from monarch_py.api.main import app
from monarch_py.service.dismech_store import DismechStore

WILSON = "MONDO:0010200"
OTHER = "MONDO:0000001"
ONLY_DISMECH = "MONDO:0000002"
LIVER = "HP:0001392"
CIRRHOSIS = "HP:0001394"
JAUNDICE = "HP:0000952"
N = "dismech:Wilson_Disease#"


def ev(ref="PMID:1"):
    return {"reference": ref, "title": None, "supports": "SUPPORT", "source": None, "snippet": "s"}


def record(mondo, hpo, name, disorder="Wilson Disease", file="Wilson_Disease", diagnostic=False, edges=()):
    return {
        "mondo_id": mondo,
        "disorder": disorder,
        "disorder_file": file,
        "phenotype_name": name,
        "phenotype_node_id": f"dismech:{file}#{name}",
        "hpo_id": hpo,
        "hpo_label": name,
        "frequency_hp": "HP:0040281",
        "frequency_text": None,
        "diagnostic": diagnostic,
        "evidence": [ev()],
        "nearest_mechanisms": ["Copper"],
        "upstream_edges": [{"source": s, "target": t, "link_type": "DIRECT"} for s, t in edges],
    }


def kg_edge(subject, subject_label, obj, obj_label, source, negated=None, count=None, total=None):
    return {
        "subject_key": int(subject.split(":")[1]),
        "object_key": int(obj.split(":")[1]),
        "subject": subject,
        "subject_label": subject_label,
        "object": obj,
        "object_label": obj_label,
        "negated": negated,
        "primary_knowledge_source": source,
        "original_subject": "OMIM:277900",
        "frequency_qualifier": "HP:0040281" if count is None else None,
        "frequency_qualifier_label": "Very frequent" if count is None else None,
        "has_percentage": None,
        "has_count": count,
        "has_total": total,
        "onset_qualifier_label": None,
        "sex_qualifier_label": None,
        "publications": ["PMID:2"],
        "has_evidence": [],
    }


TABLES = {
    "core.release": [{"release": "v0.1.47"}],
    "core.phenotype": [
        # cirrhosis is a subclass of the KG's liver abnormality: corroborates it as more_specific
        record(WILSON, CIRRHOSIS, "Cirrhosis", diagnostic=True, edges=[(f"{N}Copper", f"{N}Cirrhosis")]),
        record(WILSON, JAUNDICE, "Jaundice"),
        record(ONLY_DISMECH, CIRRHOSIS, "Cirrhosis", disorder="Rare Disease", file="Rare_Disease"),
    ],
    "core.node": [
        {
            "node_id": f"{N}Copper",
            "kind": "mechanism",
            "name": "Copper",
            "term_id": None,
            "description": "copper builds up",
            "biological_scale": "CELLULAR",
            "frequency": None,
            "descriptors": [{"slot": "cell_types", "id": "CL:0000182", "label": "hepatocyte", "modifier": None}],
            "evidence": [ev()],
        },
        {
            "node_id": f"{N}Cirrhosis",
            "kind": "phenotype",
            "name": "Cirrhosis",
            "term_id": CIRRHOSIS,
            "description": None,
            "biological_scale": None,
            "frequency": "VERY_FREQUENT",
            "descriptors": [],
            "evidence": [],
        },
    ],
    "core.phenotype_mechanism": [
        {
            "node_id": f"{N}Copper",
            "phenotype_node_id": f"{N}Cirrhosis",
            "mondo_id": WILSON,
            "hpo_id": CIRRHOSIS,
            "hpo_label": "Cirrhosis",
            "diagnostic": True,
        }
    ],
    "core.descriptor": [
        {
            "mondo_id": WILSON,
            "disorder": "Wilson Disease",
            "disorder_file": "Wilson_Disease",
            "node_id": f"{N}Copper",
            "node_name": "Copper",
            "slot": "cell_types",
            "term_id": "CL:0000182",
            "term_label": "hepatocyte",
            "modifier": None,
        }
    ],
    "core.treatment": [
        {
            "mondo_id": WILSON,
            "disorder": "Wilson Disease",
            "disorder_file": "Wilson_Disease",
            "treatment_node_id": f"{N}Trientine",
            "name": "Trientine",
            "description": "chelator",
            "modality": "SMALL_MOLECULE",
            "action_category": None,
            "treatment_term_id": None,
            "treatment_term_label": None,
            "agents": [{"id": "CHEBI:39501", "label": None}, {"id": "NCIT:C1", "label": "thing"}],
            "target_mechanisms": [
                {
                    "node_id": f"{N}Copper",
                    "name": "Copper",
                    "resolved": True,
                    "effect": "INHIBITS",
                    "description": None,
                    "evidence": [],
                }
            ],
            "target_phenotypes": [{"hpo_id": CIRRHOSIS, "label": "Cirrhosis"}],
            "evidence": [ev()],
        }
    ],
    "core.pathograph_disorder": [
        {"mondo_id": WILSON, "file": "MONDO_0010200.json", "name": "Wilson Disease", "slug": "Wilson_Disease"}
    ],
    "core.pathograph_node": [
        {
            "file": "MONDO_0010200.json",
            "ord": 0,
            "id": "ATP7B",
            "node_type": "genetic",
            "color": None,
            "is_orphan": False,
            "description": None,
            "meta": json.dumps({"gene_terms": [{"id": "hgnc:870", "label": "ATP7B"}]}),
        },
        {
            "file": "MONDO_0010200.json",
            "ord": 1,
            "id": "Cirrhosis",
            "node_type": "phenotype",
            "color": None,
            "is_orphan": False,
            "description": None,
            "meta": json.dumps({"term_id": CIRRHOSIS}),
        },
    ],
    "core.pathograph_edge": [
        {
            "file": "MONDO_0010200.json",
            "ord": 0,
            "source": "ATP7B",
            "target": "Cirrhosis",
            "predicate": "causes",
            "description": None,
        }
    ],
    "core.pathograph_gene": [{"gene_id": "HGNC:870", "mondo_id": WILSON}],
    "app.kg_disease_phenotype": [
        kg_edge(WILSON, "Wilson disease", LIVER, "Abnormality of the liver", "infores:omim", count=1, total=1),
        kg_edge(WILSON, "Wilson disease", LIVER, "Abnormality of the liver", "infores:orphanet"),
        kg_edge(WILSON, "Wilson disease", JAUNDICE, "Jaundice", "infores:orphanet"),
        kg_edge(OTHER, "other disease", CIRRHOSIS, "Cirrhosis", "infores:orphanet"),
        kg_edge(ONLY_DISMECH, "rare disease", LIVER, "Abnormality of the liver", "infores:orphanet"),
    ],
    "app.hp_closure": [
        {"ancestor_key": 1392, "hpo_id": CIRRHOSIS, "ancestor_id": LIVER},
        {"ancestor_key": 1394, "hpo_id": CIRRHOSIS, "ancestor_id": CIRRHOSIS},
        {"ancestor_key": 1392, "hpo_id": LIVER, "ancestor_id": LIVER},
        {"ancestor_key": 952, "hpo_id": JAUNDICE, "ancestor_id": JAUNDICE},
    ],
    "app.kg_node": [
        {"id": "CHEBI:39501", "name": "trientine", "category": "biolink:ChemicalEntity"},
        {"id": "CL:0000182", "name": "hepatocyte", "category": "biolink:Cell"},
    ],
}
TABLES["app.kg_phenotype_disease"] = TABLES["app.kg_disease_phenotype"]


@pytest.fixture(scope="module")
def store(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("dismech")
    path = tmp / "dismech.duckdb"
    con = duckdb.connect(str(path))
    con.execute("CREATE SCHEMA core")
    con.execute("CREATE SCHEMA app")
    for name, rows in TABLES.items():
        lines = tmp / f"{name}.jsonl"
        lines.write_text("\n".join(json.dumps(r) for r in rows))
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM read_json(?, format='newline_delimited')", [str(lines)])
    con.close()
    return DismechStore.open(str(path))


def by_id(rows, key):
    return {r[key]: r for r in rows}


def test_profile_collapses_kg_sources_and_attaches_more_specific_dismech(store):
    profile = store.phenotype_profile(WILSON)
    assert profile["release"] == "v0.1.47"
    rows = by_id(profile["rows"], "hpo_id")
    liver = rows[LIVER]
    assert liver["sources"] == ["infores:omim", "infores:orphanet"]
    assert [(m["match"], m["hpo_id"]) for m in liver["dismech"]] == [("more_specific", CIRRHOSIS)]
    assert [m["match"] for m in rows[JAUNDICE]["dismech"]] == ["exact"]


def test_profile_ranks_diagnostic_first(store):
    assert store.phenotype_profile(WILSON)["rows"][0]["hpo_id"] == LIVER


def test_profile_mechanism_nodes_cover_the_upstream_chain(store):
    nodes = store.phenotype_profile(WILSON)["mechanism_nodes"]
    assert nodes[f"{N}Copper"]["descriptors"][0]["id"] == "CL:0000182"
    assert nodes[f"{N}Cirrhosis"]["kind"] == "phenotype"


def test_profile_filters_and_pages(store):
    assert store.phenotype_profile(WILSON, limit=1)["total"] == 2
    assert len(store.phenotype_profile(WILSON, limit=1)["rows"]) == 1
    assert store.phenotype_profile(OTHER, corroborated_only=True)["rows"] == []


def test_dismech_only_rows_are_opt_in(store):
    profile = store.phenotype_profile(ONLY_DISMECH)
    # its cirrhosis record corroborates the KG liver row, so nothing is dismech-only
    assert profile["dismech_unmatched"] == 0
    assert [r["hpo_id"] for r in profile["rows"]] == [LIVER]


def test_phenotype_diseases_matches_records_of_subclasses(store):
    result = store.phenotype_diseases(LIVER)
    rows = by_id(result["rows"], "disease_id")
    assert set(rows) == {WILSON, ONLY_DISMECH}
    assert [m["hpo_id"] for m in rows[WILSON]["dismech"]] == [CIRRHOSIS]
    assert rows[WILSON]["label"] == "Wilson disease"


def test_phenotype_diseases_dismech_only_disease_is_labelled_from_the_kg(store):
    result = store.phenotype_diseases(CIRRHOSIS, dismech_only=True)
    rows = by_id(result["rows"], "disease_id")
    assert result["dismech_unmatched"] == 2
    assert rows[ONLY_DISMECH]["dismech_only"] is True
    assert rows[ONLY_DISMECH]["label"] == "rare disease"
    assert rows[WILSON]["label"] == "Wilson disease"
    assert OTHER in rows and not rows[OTHER]["dismech"]


def test_treatments_for_a_disease_and_for_a_drug(store):
    [t] = store.treatments(WILSON)["rows"]
    assert {a["id"]: a["in_kg"] for a in t["agents"]} == {"CHEBI:39501": True, "NCIT:C1": False}
    assert t["agents"][0]["label"] == "trientine"
    assert [r["name"] for r in store.treatments("CHEBI:39501")["rows"]] == ["Trientine"]
    assert store.treatments("CHEBI:1")["rows"] == []


def test_mechanisms_by_term_lead_to_phenotypes(store):
    result = store.mechanisms("CL:0000182")
    assert result["label"] == "hepatocyte"
    [row] = result["rows"]
    assert row["slots"] == ["cell_types"]
    assert [p["hpo_id"] for p in row["leads_to"]] == [CIRRHOSIS]


def test_pathograph_graphs_by_disease_and_gene(store):
    [(mondo, name, slug, graph)] = store.pathograph_graphs(WILSON)
    assert (mondo, name, slug) == (WILSON, "Wilson Disease", "Wilson_Disease")
    assert graph["nodes"][0]["meta"] == {"gene_terms": [{"id": "hgnc:870", "label": "ATP7B"}]}
    assert graph["edges"] == [{"source": "ATP7B", "target": "Cirrhosis", "predicate": "causes", "description": None}]
    assert [g[0] for g in store.pathograph_graphs("HGNC:870")] == [WILSON]
    assert store.pathograph_graphs("HGNC:1") == []


@pytest.fixture
def client(store, monkeypatch):
    monkeypatch.setattr(dismech_route, "dismech_store", lambda: store)
    monkeypatch.setattr(pathograph_route, "dismech_store", lambda: store)
    return TestClient(app)


def test_pathograph_route_reads_the_store(client):
    body = client.get("/v3/api/pathograph/hgnc:870").json()
    assert body["category"] == "gene"
    assert {n["id"] for n in body["nodes"]} == {"HGNC:870", CIRRHOSIS}
    assert body["sources"][0]["url"].endswith("/pages/disorders/Wilson_Disease.html")
    assert client.get("/v3/api/pathograph/MONDO:0000009").status_code == 404


def test_dismech_routes(client):
    assert client.get(f"/v3/api/dismech/phenotype-profile/{WILSON}").json()["total"] == 2
    assert client.get(f"/v3/api/dismech/phenotype-diseases/{LIVER}").json()["total"] == 2
    assert len(client.get(f"/v3/api/dismech/treatments/{WILSON}").json()["rows"]) == 1
    assert client.get("/v3/api/dismech/mechanisms/CL:0000182").json()["label"] == "hepatocyte"


def test_dismech_routes_validate_ids(client):
    assert client.get(f"/v3/api/dismech/phenotype-profile/{LIVER}").status_code == 400
    assert client.get(f"/v3/api/dismech/phenotype-diseases/{WILSON}").status_code == 400
    assert client.get("/v3/api/dismech/mechanisms/MONDO:1").status_code == 400


def test_dismech_routes_404_when_unconfigured(monkeypatch):
    monkeypatch.setattr(dismech_route, "dismech_store", lambda: None)
    assert TestClient(app).get(f"/v3/api/dismech/treatments/{WILSON}").status_code == 404
