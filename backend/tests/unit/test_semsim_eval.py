"""The simulated-patient evaluation harness, on a tiny synthetic KG.

Ontology: A1 < A < R, B1 < B < R, C1 < C < R (all HP terms). Diseases: MONDO:1 -> {A1, B1},
MONDO:2 -> {A1}, MONDO:3 -> {B1, C1}. Gene HGNC:1 causes MONDO:1. A few decoys (an OMIM disease,
an MP phenotype, an MP subclass edge, an NCBIGene cause) check that the harness keeps to MONDO and HP.
"""

import duckdb
import pytest

from monarch_py.service.ducksim import Ducksim
from monarch_py.utils.semsim_eval import CONFIGS, EvalOptions, SemsimEvaluation, format_summary, summarize

D2P = "biolink:DiseaseToPhenotypicFeatureAssociation"
G2P = "biolink:GeneToPhenotypicFeatureAssociation"
R, A, A1, B, B1, C, C1 = (f"HP:000000{i}" for i in range(1, 8))
TERMS = {A1: A, B1: B, C1: C, A: R, B: R, C: R}
OCCASIONAL, VERY_RARE = "HP:0040283", "HP:0040284"


@pytest.fixture
def engine(tmp_path):
    path = str(tmp_path / "kg.duckdb")
    con = duckdb.connect(path)
    closure = [(R, R)] + [(t, t) for t in TERMS]
    for term in TERMS:
        node = term
        while node in TERMS:
            closure.append((term, TERMS[node]))
            node = TERMS[node]
    con.execute("CREATE TABLE closure(subject_id VARCHAR, predicate_id VARCHAR, object_id VARCHAR)")
    con.executemany("INSERT INTO closure VALUES (?, 'rdfs:subClassOf', ?)", sorted(set(closure)))
    con.execute(
        "CREATE TABLE edges(subject VARCHAR, object VARCHAR, category VARCHAR, predicate VARCHAR, negated VARCHAR, "
        "has_quotient DOUBLE, frequency_qualifier VARCHAR)"
    )
    # (subject, object, has_quotient, frequency_qualifier). MONDO:1 records A1 as occasional, so the
    # frequency tie-break puts MONDO:2 (no frequency, so the default 0.5) ahead of it for a query of A1.
    has_phenotype = [
        ("MONDO:1", A1, None, OCCASIONAL),
        ("MONDO:1", B1, None, None),
        ("MONDO:2", A1, None, None),
        ("MONDO:3", B1, 0.9, None),
        ("MONDO:3", C1, None, VERY_RARE),
        ("MONDO:1", "MP:0000001", None, None),
        ("OMIM:100000", C1, None, None),
    ]
    con.executemany(f"INSERT INTO edges VALUES (?, ?, '{D2P}', 'biolink:has_phenotype', NULL, ?, ?)", has_phenotype)
    con.executemany(
        f"INSERT INTO edges VALUES ('HGNC:1', ?, '{G2P}', 'biolink:has_phenotype', NULL, NULL, NULL)", [(A1,), (B1,)]
    )
    causes = "'biolink:CausalGeneToDiseaseAssociation', 'biolink:causes', NULL, NULL, NULL"
    con.execute(f"INSERT INTO edges VALUES ('HGNC:1', 'MONDO:1', {causes})")
    con.execute(f"INSERT INTO edges VALUES ('NCBIGene:1', 'MONDO:3', {causes})")
    con.executemany(
        "INSERT INTO edges VALUES (?, ?, 'biolink:SubclassOf', 'biolink:subclass_of', NULL, NULL, NULL)",
        [(c, p) for c, p in TERMS.items()] + [("MP:0000001", "MP:0000002")],
    )
    con.execute("CREATE TABLE nodes(id VARCHAR, name VARCHAR)")
    con.execute(
        """CREATE TABLE information_content AS
        WITH clo AS (SELECT object_id AS o FROM closure), n AS (SELECT count(DISTINCT o) AS nn FROM clo)
        SELECT o AS term, -log2(count(*)::DOUBLE / (SELECT nn FROM n)) AS ic FROM clo GROUP BY o"""
    )
    con.execute(
        """CREATE TABLE closure_size AS
        SELECT e.subject AS entity, count(DISTINCT c.object_id) AS size
        FROM edges e JOIN closure c ON c.subject_id = e.object WHERE e.predicate = 'biolink:has_phenotype'
        GROUP BY e.subject"""
    )
    con.close()
    return Ducksim.from_duckdb(path)


def _options(**kw):
    defaults = dict(sample=3, min_terms=1, query_size=2, common_count=1, configs=["production", "query_to_entity"])
    return EvalOptions(**{**defaults, **kw})


def test_data_loading_keeps_to_mondo_and_hp(engine):
    evaluation = SemsimEvaluation(engine, _options())
    assert evaluation.profiles == {"MONDO:1": [A1, B1], "MONDO:2": [A1], "MONDO:3": [B1, C1]}
    assert evaluation.parents == {term: [parent] for term, parent in TERMS.items()}
    assert evaluation.term_counts == {A1: 2, B1: 2, C1: 1}


def test_exact_profile_queries_find_the_disease(engine):
    rows = SemsimEvaluation(engine, _options(kinds=["random"])).run()
    assert {r.config for r in rows} == {"production", "query_to_entity"}
    by_disease = {(r.disease, r.config): r for r in rows}
    # MONDO:1's full profile {A1, B1} is matched exactly only by MONDO:1 in the query-to-entity direction
    assert by_disease[("MONDO:1", "query_to_entity")].position == 1
    assert by_disease[("MONDO:1", "query_to_entity")].tie_size == 1


def test_gene_target_counts_causal_genes_as_answers(engine):
    evaluation = SemsimEvaluation(engine, _options(target_prefix="HGNC", kinds=["random"]))
    assert evaluation.answers == {"MONDO:1": ["HGNC:1"]}
    rows = evaluation.run()
    assert {r.disease for r in rows} == {"MONDO:1"}
    assert all(r.position == 1 for r in rows)


def test_noise_models_change_the_query(engine):
    evaluation = SemsimEvaluation(engine, _options(parent_rate=1.0))
    assert sorted(evaluation.build_query("MONDO:1", "random", "parent")) == [A, B]
    noisy = evaluation.build_query("MONDO:2", "random", "other_disease")
    assert noisy[0] == A1 and set(noisy[1:]) <= {B1, C1}
    assert evaluation.build_query("MONDO:3", "rare_alone", "none") == [C1]


def test_every_noise_model_starts_from_the_same_base_query(engine):
    evaluation = SemsimEvaluation(engine, _options(query_size=1, parent_rate=0.0))
    for disease in evaluation.profiles:
        base = evaluation.build_query(disease, "random", "none")
        assert evaluation.build_query(disease, "random", "parent") == base
        assert evaluation.build_query(disease, "random", "other_disease")[: len(base)] == base


def test_queries_do_not_depend_on_the_other_options(engine):
    narrow = SemsimEvaluation(engine, _options(kinds=["random"], noise=["none"]))
    wide = SemsimEvaluation(engine, _options(kinds=["rare_alone", "random"], noise=["parent", "none"]))
    query = lambda rows: {(r.disease, r.kind, r.noise, r.config): r.query for r in rows}
    narrow_queries = query(narrow.run())
    wide_queries = query(wide.run())
    assert narrow_queries == {k: v for k, v in wide_queries.items() if k in narrow_queries}
    assert query(narrow.run()) == narrow_queries  # a second run repeats the first


def test_rarest_term_tie_is_broken_by_the_seed(engine):
    # MONDO:1's terms A1 and B1 each annotate two diseases
    picks = {
        SemsimEvaluation(engine, _options(seed=seed)).build_query("MONDO:1", "rare_alone", "none")[0]
        for seed in range(20)
    }
    assert picks == {A1, B1}
    common_rare = SemsimEvaluation(engine, _options()).build_query("MONDO:1", "common_rare", "none")
    assert sorted(common_rare) == [A1, B1]


def test_random_weighted_prefers_frequent_terms(engine):
    # MONDO:3: B1 in 90% of patients, C1 very rare (2.5%)
    picks = [
        SemsimEvaluation(engine, _options(seed=seed, query_size=1)).build_query("MONDO:3", "random_weighted", "none")
        for seed in range(100)
    ]
    assert all(len(p) == 1 for p in picks)
    assert sum(p == [B1] for p in picks) > 80
    both = SemsimEvaluation(engine, _options(query_size=5)).build_query("MONDO:3", "random_weighted", "none")
    assert sorted(both) == [B1, C1]


def test_random_weighted_samples_terms_recorded_in_no_patients(engine, monkeypatch):
    monkeypatch.setattr(engine, "frequencies_batch", lambda ids: {("MONDO:3", B1): 0.0, ("MONDO:3", C1): 0.0})
    query = SemsimEvaluation(engine, _options(query_size=5)).build_query("MONDO:3", "random_weighted", "none")
    assert sorted(query) == [B1, C1]


def test_frequency_tie_break_reorders_tied_diseases(engine):
    evaluation = SemsimEvaluation(engine, _options())
    # MONDO:1 and MONDO:2 both match A1 exactly. By id MONDO:1 comes first; by frequency MONDO:2
    # (default 0.5) beats MONDO:1's occasional 0.17.
    assert evaluation.rank([A1], ["MONDO:1"], CONFIGS["query_to_entity"])[:2] == (1, 2)
    assert evaluation.rank([A1], ["MONDO:1"], CONFIGS["query_to_entity_frequency"])[:2] == (2, 2)


def test_summary_table(engine):
    rows = SemsimEvaluation(engine, _options(kinds=["random", "rare_alone"])).run()
    summary = summarize(rows)
    assert {(s["kind"], s["config"]) for s in summary} == {
        (k, c) for k in ("random", "rare_alone") for c in ("production", "query_to_entity")
    }
    assert all(0 <= s["top1"] <= s["top10"] <= 1 for s in summary)
    assert format_summary(summary).startswith("| query | noise | setting |")


def test_summary_cuts_every_setting_at_the_same_depth(engine):
    rows = SemsimEvaluation(engine, _options(kinds=["random"])).run()
    for row in rows:
        row.position = 3
    shallow = summarize(rows, depth=2)
    assert all(s["mrr"] == 0 and s["median_position"] == float("inf") for s in shallow)
    assert "| >2 |" in format_summary(shallow)
    assert all(s["mrr"] == pytest.approx(1 / 3) for s in summarize(rows, depth=10))


def test_every_config_is_a_valid_engine_setting():
    for config in CONFIGS.values():
        assert set(config) == {"mode", "direction", "information_content", "tie_break"}
