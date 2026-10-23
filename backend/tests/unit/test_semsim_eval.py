"""The simulated-patient evaluation harness, on a tiny synthetic KG.

Ontology: A1 < A < R, B1 < B < R, C1 < C < R. Diseases: MONDO:1 -> {A1, B1}, MONDO:2 -> {A1},
MONDO:3 -> {B1, C1}. Gene HGNC:1 causes MONDO:1.
"""

import duckdb
import pytest

from monarch_py.service.ducksim import Ducksim
from monarch_py.utils.semsim_eval import CONFIGS, EvalOptions, SemsimEvaluation, format_summary, summarize

D2P = "biolink:DiseaseToPhenotypicFeatureAssociation"
G2P = "biolink:GeneToPhenotypicFeatureAssociation"
TERMS = {"A1": "A", "B1": "B", "C1": "C", "A": "R", "B": "R", "C": "R"}


@pytest.fixture
def engine(tmp_path):
    path = str(tmp_path / "kg.duckdb")
    con = duckdb.connect(path)
    closure = [("R", "R")] + [(t, t) for t in TERMS]
    for term in TERMS:
        node = term
        while node in TERMS:
            closure.append((term, TERMS[node]))
            node = TERMS[node]
    con.execute("CREATE TABLE closure(subject_id VARCHAR, predicate_id VARCHAR, object_id VARCHAR)")
    con.executemany("INSERT INTO closure VALUES (?, 'rdfs:subClassOf', ?)", sorted(set(closure)))
    con.execute(
        "CREATE TABLE edges(subject VARCHAR, object VARCHAR, category VARCHAR, predicate VARCHAR, negated VARCHAR)"
    )
    has_phenotype = [("MONDO:1", "A1"), ("MONDO:1", "B1"), ("MONDO:2", "A1"), ("MONDO:3", "B1"), ("MONDO:3", "C1")]
    con.executemany(f"INSERT INTO edges VALUES (?, ?, '{D2P}', 'biolink:has_phenotype', NULL)", has_phenotype)
    con.execute(f"INSERT INTO edges VALUES ('HGNC:1', 'A1', '{G2P}', 'biolink:has_phenotype', NULL)")
    con.execute(f"INSERT INTO edges VALUES ('HGNC:1', 'B1', '{G2P}', 'biolink:has_phenotype', NULL)")
    con.execute(
        "INSERT INTO edges VALUES ('HGNC:1', 'MONDO:1', 'biolink:CausalGeneToDiseaseAssociation', 'biolink:causes', NULL)"
    )
    con.executemany(
        "INSERT INTO edges VALUES (?, ?, 'biolink:SubclassOf', 'biolink:subclass_of', NULL)",
        [(c, p) for c, p in TERMS.items()],
    )
    con.execute("CREATE TABLE nodes(id VARCHAR, name VARCHAR)")
    con.execute("""CREATE TABLE information_content AS
        WITH clo AS (SELECT object_id AS o FROM closure), n AS (SELECT count(DISTINCT o) AS nn FROM clo)
        SELECT o AS term, -log2(count(*)::DOUBLE / (SELECT nn FROM n)) AS ic FROM clo GROUP BY o""")
    con.execute("""CREATE TABLE closure_size AS
        SELECT e.subject AS entity, count(DISTINCT c.object_id) AS size
        FROM edges e JOIN closure c ON c.subject_id = e.object WHERE e.predicate = 'biolink:has_phenotype'
        GROUP BY e.subject""")
    con.close()
    return Ducksim.from_duckdb(path)


@pytest.fixture
def hp_terms(monkeypatch):
    """The harness restricts profiles and parents to HP terms; let the fixture's bare terms through."""
    monkeypatch.setattr(
        SemsimEvaluation,
        "_disease_profiles",
        lambda self: {
            e: sorted(p for (p,) in self._rows(f"SELECT phenotype FROM _assoc WHERE entity = '{e}'"))
            for e in ("MONDO:1", "MONDO:2", "MONDO:3")
        },
    )
    monkeypatch.setattr(SemsimEvaluation, "_direct_parents", lambda self: {c: [p] for c, p in TERMS.items()})


def _options(**kw):
    defaults = dict(sample=3, min_terms=1, query_size=2, common_count=1, configs=["production", "query_to_entity"])
    return EvalOptions(**{**defaults, **kw})


def test_exact_profile_queries_find_the_disease(engine, hp_terms):
    rows = SemsimEvaluation(engine, _options(kinds=["random"])).run()
    assert {r.config for r in rows} == {"production", "query_to_entity"}
    by_disease = {(r.disease, r.config): r for r in rows}
    # MONDO:1's full profile {A1, B1} is matched exactly only by MONDO:1 in the query-to-entity direction
    assert by_disease[("MONDO:1", "query_to_entity")].position == 1
    assert by_disease[("MONDO:1", "query_to_entity")].tie_size == 1


def test_gene_target_counts_causal_genes_as_answers(engine, hp_terms):
    evaluation = SemsimEvaluation(engine, _options(target_prefix="HGNC", kinds=["random"]))
    assert evaluation.answers == {"MONDO:1": ["HGNC:1"]}
    rows = evaluation.run()
    assert {r.disease for r in rows} == {"MONDO:1"}
    assert all(r.position == 1 for r in rows)


def test_noise_models_change_the_query(engine, hp_terms):
    evaluation = SemsimEvaluation(engine, _options(parent_rate=1.0))
    assert sorted(evaluation.build_query("MONDO:1", "random", "parent")) == ["A", "B"]
    noisy = evaluation.build_query("MONDO:2", "random", "unrelated")
    assert noisy[0] == "A1" and set(noisy[1:]) <= {"B1", "C1"}
    assert evaluation.build_query("MONDO:3", "rare_alone", "none") == ["C1"]


def test_summary_table(engine, hp_terms):
    rows = SemsimEvaluation(engine, _options(kinds=["random", "rare_alone"])).run()
    summary = summarize(rows)
    assert {(s["kind"], s["config"]) for s in summary} == {
        (k, c) for k in ("random", "rare_alone") for c in ("production", "query_to_entity")
    }
    assert all(0 <= s["top1"] <= s["top10"] <= 1 for s in summary)
    assert format_summary(summary).startswith("| query | noise | setting |")


def test_every_config_is_a_valid_engine_setting():
    for config in CONFIGS.values():
        assert set(config) == {"mode", "direction", "information_content", "tie_break"}
