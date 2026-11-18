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
from monarch_py.service.phenotype_profile import frequency_score

WILSON = "MONDO:0010200"
OTHER = "MONDO:0000001"
ONLY_DISMECH = "MONDO:0000002"
NEGATED = "MONDO:0000003"
LIVER = "HP:0001392"
CIRRHOSIS = "HP:0001394"
JAUNDICE = "HP:0000952"
DIGESTIVE = "UPHENO:0002443"
LIVER_ORGAN = "UBERON:0002107"
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


def gene_record(gene, symbol, relationship, kind):
    return {
        "gene_id": gene,
        "symbol": symbol,
        "name": symbol,
        "mondo_id": WILSON,
        "disorder": "Wilson Disease",
        "disorder_file": "Wilson_Disease",
        "relationship_type": relationship,
        "association": None,
        "kind": kind,
        "variant_origin": None,
        "validity": [{"classification": "DEFINITIVE", "classified_by": "CLINGEN"}],
        "notes": None,
        "evidence": [ev()],
    }


def gene_edge(gene, symbol, category, source):
    return {
        "subject_key": int(gene.split(":")[1]),
        "object_key": 10200,
        "subject": gene,
        "subject_label": symbol,
        "object": WILSON,
        "object_label": "Wilson disease",
        "category": f"biolink:{category}GeneToDiseaseAssociation",
        "predicate": "biolink:causes",
        "primary_knowledge_source": source,
        "original_subject": None,
        "publications": [],
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
        },
        {
            "mondo_id": WILSON,
            "disorder": "Wilson Disease",
            "disorder_file": "Wilson_Disease",
            "node_id": f"{N}Copper",
            "node_name": "Copper",
            "slot": "genes",
            "term_id": "HGNC:870",
            "term_label": "ATP7B",
            "modifier": None,
        },
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
        kg_edge(NEGATED, "negated disease", CIRRHOSIS, "Cirrhosis", "infores:omim", negated=True),
    ],
    "app.hp_closure": [
        {"ancestor_key": 1392, "hpo_id": CIRRHOSIS, "ancestor_id": LIVER},
        {"ancestor_key": 1394, "hpo_id": CIRRHOSIS, "ancestor_id": CIRRHOSIS},
        {"ancestor_key": 1392, "hpo_id": LIVER, "ancestor_id": LIVER},
        {"ancestor_key": 952, "hpo_id": JAUNDICE, "ancestor_id": JAUNDICE},
        {"ancestor_key": 2443, "hpo_id": LIVER, "ancestor_id": DIGESTIVE},
        {"ancestor_key": 2443, "hpo_id": CIRRHOSIS, "ancestor_id": DIGESTIVE},
        {"ancestor_key": 2107, "hpo_id": LIVER, "ancestor_id": LIVER_ORGAN},
        {"ancestor_key": 2107, "hpo_id": CIRRHOSIS, "ancestor_id": LIVER_ORGAN},
    ],
    "app.kg_node": [
        {"id": "CHEBI:39501", "name": "trientine", "category": "biolink:ChemicalEntity"},
        {"id": "CL:0000182", "name": "hepatocyte", "category": "biolink:Cell"},
        {"id": WILSON, "name": "Wilson disease", "category": "biolink:Disease"},
        {"id": "HGNC:999", "name": "GENE9", "category": "biolink:Gene"},
    ],
    "core.gene": [
        gene_record("HGNC:870", "ATP7B", "CAUSATIVE", "causal"),
        # dismech calls it causal, the KG only correlated: corroborates the correlated row
        gene_record("HGNC:111", "MOD1", "CAUSATIVE", "causal"),
        # in neither KG category: dismech-only, in dismech's category
        gene_record("HGNC:999", "GENE9", "SUSCEPTIBILITY", "correlated"),
    ],
    "app.kg_gene_disease": [
        gene_edge("HGNC:870", "ATP7B", "Causal", "infores:omim"),
        gene_edge("HGNC:870", "ATP7B", "Causal", "infores:clingen"),
        gene_edge("HGNC:111", "MOD1", "Correlated", "infores:orphanet"),
    ],
}
TABLES["app.kg_phenotype_disease"] = TABLES["app.kg_disease_phenotype"]
TABLES["app.kg_disease_gene"] = TABLES["app.kg_gene_disease"]


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
    assert set(rows) == {WILSON, OTHER, ONLY_DISMECH, NEGATED}
    assert [m["hpo_id"] for m in rows[WILSON]["dismech"]] == [CIRRHOSIS]
    assert rows[WILSON]["label"] == "Wilson disease"


def test_phenotype_diseases_rolls_up_kg_annotations_of_subclasses(store):
    rows = by_id(store.phenotype_diseases(LIVER)["rows"], "disease_id")
    assert rows[OTHER]["dismech_only"] is False
    assert [(o["phenotype"], o["phenotype_label"]) for o in rows[OTHER]["observations"]] == [(CIRRHOSIS, "Cirrhosis")]
    # kept, as the stock table keeps it; the row says which term is negated
    assert rows[NEGATED]["negated"] is True
    assert [o["phenotype"] for o in rows[NEGATED]["observations"]] == [CIRRHOSIS]


def test_phenotype_diseases_scores_like_the_profile(store):
    rows = by_id(store.phenotype_diseases(LIVER)["rows"], "disease_id")
    assert rows[WILSON]["frequency_score"] == pytest.approx(frequency_score(rows[WILSON]))


def test_phenotype_diseases_loads_only_the_page(store):
    result = store.phenotype_diseases(LIVER, limit=1)
    assert result["total"] == 4 and len(result["rows"]) == 1
    assert result["rows"][0]["observations"]


def test_phenotype_diseases_keeps_negated_annotations_of_the_term_itself(store):
    rows = store.phenotype_diseases(CIRRHOSIS)["rows"]
    assert [r["negated"] for r in rows if r["disease_id"] == NEGATED] == [True]


@pytest.mark.parametrize("term", [DIGESTIVE, LIVER_ORGAN])
def test_phenotype_diseases_for_upheno_and_anatomy_terms(store, term):
    rows = by_id(store.phenotype_diseases(term)["rows"], "disease_id")
    assert set(rows) == {WILSON, OTHER, ONLY_DISMECH, NEGATED}
    assert {m["hpo_id"] for m in rows[WILSON]["dismech"]} == {CIRRHOSIS}


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


def test_treatments_carry_the_graph_downstream_of_their_targets(store):
    result = store.treatments(WILSON)
    [t] = result["rows"]
    assert [p["hpo_id"] for p in t["leads_to"]] == [CIRRHOSIS]
    assert [(e["source"], e["target"]) for e in t["edges"]] == [(f"{N}Copper", f"{N}Cirrhosis")]
    assert {f"{N}Copper", f"{N}Cirrhosis"} <= set(result["mechanism_nodes"])


def test_treatments_match_a_drug_by_name(store):
    # dismech often names a drug without an agent term
    assert [r["name"] for r in store.treatments("RXCUI:1", name="trientine")["rows"]] == ["Trientine"]
    assert store.treatments("RXCUI:1", name="tri")["rows"] == []


def test_term_diseases_one_row_per_disease(store):
    result = store.term_diseases("CL:0000182")
    assert (result["label"], result["total"]) == ("hepatocyte", 1)
    [row] = result["rows"]
    assert (row["disease_id"], row["label"], row["slots"]) == (WILSON, "Wilson disease", ["cell_types"])
    assert [m["name"] for m in row["mechanisms"]] == ["Copper"]
    assert [p["hpo_id"] for p in row["leads_to"]] == [CIRRHOSIS]
    assert row["leads_to"][0]["diagnostic"] is True
    assert [(e["source"], e["target"]) for e in row["edges"]] == [(f"{N}Copper", f"{N}Cirrhosis")]


def test_gene_profile_collapses_sources_and_attaches_mechanisms(store):
    result = store.gene_disease_profile("HGNC:870", "causal")
    [row] = result["rows"]
    assert (row["disease_id"], row["sources"]) == (WILSON, ["infores:clingen", "infores:omim"])
    [rec] = row["dismech"]
    assert [m["name"] for m in rec["mechanisms"]] == ["Copper"]
    assert [p["hpo_id"] for p in rec["leads_to"]] == [CIRRHOSIS]
    assert f"{N}Copper" in result["mechanism_nodes"]


def test_gene_profile_from_a_disease_page(store):
    causal = store.gene_disease_profile(WILSON, "causal", dismech_only=True)
    assert [r["gene_id"] for r in causal["rows"]] == ["HGNC:870"]
    correlated = store.gene_disease_profile(WILSON, "correlated", dismech_only=True)
    rows = {r["gene_id"]: r for r in correlated["rows"]}
    # dismech says causal but the KG has the pair as correlated: corroborates that row
    assert rows["HGNC:111"]["dismech"][0]["relationship_type"] == "CAUSATIVE"
    assert rows["HGNC:999"]["dismech_only"] is True
    assert rows["HGNC:999"]["label"] == "GENE9"
    assert store.gene_disease_profile(WILSON, "correlated")["dismech_unmatched"] == 1
    assert "HGNC:999" not in {r["gene_id"] for r in store.gene_disease_profile(WILSON, "correlated")["rows"]}


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
    assert client.get(f"/v3/api/dismech/phenotype-diseases/{LIVER}").json()["total"] == 4
    assert client.get(f"/v3/api/dismech/phenotype-diseases/{LIVER_ORGAN}").json()["total"] == 4
    assert len(client.get(f"/v3/api/dismech/treatments/{WILSON}").json()["rows"]) == 1
    assert client.get("/v3/api/dismech/term-diseases/CL:0000182").json()["total"] == 1
    assert client.get("/v3/api/dismech/gene-disease-profile/HGNC:870").json()["total"] == 1


def test_dismech_routes_validate_ids(client):
    assert client.get(f"/v3/api/dismech/phenotype-profile/{LIVER}").status_code == 400
    assert client.get(f"/v3/api/dismech/phenotype-diseases/not-a-curie").status_code == 400
    assert client.get("/v3/api/dismech/term-diseases/CHEBI:1").status_code == 400
    assert client.get("/v3/api/dismech/gene-disease-profile/HP:0000001").status_code == 400
    assert client.get("/v3/api/dismech/gene-disease-profile/HGNC:870?kind=other").status_code == 422


def test_status_reports_the_release(client):
    assert client.get("/v3/api/dismech/status").json() == {"release": "v0.1.47"}


def test_dismech_routes_404_when_unconfigured(monkeypatch):
    monkeypatch.setattr(dismech_route, "dismech_store", lambda: None)
    assert TestClient(app).get("/v3/api/dismech/status").status_code == 404
    assert TestClient(app).get(f"/v3/api/dismech/treatments/{WILSON}").status_code == 404


def test_phenotype_diseases_search_matches_labels_and_annotated_subclasses(store):
    def ids(**kw):
        return {r["disease_id"] for r in store.phenotype_diseases(LIVER, dismech_only=True, **kw)["rows"]}

    assert ids(search="wilson") == {WILSON}
    # OTHER is under the liver page through its cirrhosis annotation
    assert ids(search="CIRRH") >= {OTHER}
    assert ids(search="other cirrhosis") == {OTHER}
    assert ids(search="no such thing") == set()
    result = store.phenotype_diseases(LIVER, search="wilson")
    assert result["total"] == 1 and result["kg_total"] == 4


def test_profile_and_gene_tables_search(store):
    assert [r["hpo_id"] for r in store.phenotype_profile(WILSON, search="jaund")["rows"]] == [JAUNDICE]
    assert store.gene_disease_profile("HGNC:870", "causal", search="nothing")["total"] == 0


def test_dismech_routes_pass_the_search(client):
    assert client.get(f"/v3/api/dismech/phenotype-diseases/{LIVER}?search=wilson").json()["total"] == 1


def test_profile_and_gene_routes_pass_the_search(client):
    assert client.get(f"/v3/api/dismech/phenotype-profile/{WILSON}?search=jaund").json()["total"] == 1
    assert client.get("/v3/api/dismech/gene-disease-profile/HGNC:870?search=nothing").json()["total"] == 0
    assert client.get("/v3/api/dismech/gene-disease-profile/HGNC:870?search=wilson").json()["total"] == 1


@pytest.mark.parametrize("term", [LIVER, CIRRHOSIS, DIGESTIVE, LIVER_ORGAN])
def test_phenotype_diseases_has_the_stock_tables_diseases(store, term):
    """the KG rows are exactly the diseases with an edge under the term in the closure, the set
    the stock (solr object_closure) table lists"""
    under = {r["hpo_id"] for r in TABLES["app.hp_closure"] if r["ancestor_id"] == term}
    expected = {(e["subject"], bool(e["negated"])) for e in TABLES["app.kg_phenotype_disease"] if e["object"] in under}
    rows = store.phenotype_diseases(term)["rows"]
    assert {(r["disease_id"], r["negated"]) for r in rows if not r["dismech_only"]} == expected
