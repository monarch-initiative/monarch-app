"""ducksim — semantic similarity (semsimian-equivalent) computed in DuckDB.

Reads the ontology closure + KG edges directly from the read-only `monarch-kg.duckdb` artifact the
api already ships at /data, so there's no separate in-memory service holding the ontology resident.
Validated bit-exact against semsimian's committed test values and to FP precision against the live
library at scale (see the ducksim workspace; this is the production-only port — the equivalence
harness and the SQLite/phenio test backend live there, not here).

ducksim is a pure reader of the precompute tables koza's `information-content` operation bakes into
the artifact during the KG build (monarch-ingest): `information_content` (term, ic) and
`closure_size` (entity, size). It does not recompute them — a db missing them fails loud.

Metric definitions:  IC(t) = -log2(freq/N) (freq = #closure triples with t as object, N = #distinct
objects); closure is reflexive; Jaccard = |anc(a)∩anc(b)| / |anc(a)∪anc(b)|; Resnik = max IC over
shared ancestors; Phenodigm = sqrt(Resnik·Jaccard); termset score = bidirectional best-match-average.
"""

from __future__ import annotations

import math
from statistics import mean
from typing import NamedTuple

import duckdb

DEFAULT_PREDICATES = ("rdfs:subClassOf",)


class _Metric(NamedTuple):
    """How to score one semsimian metric. (Only Resnik's two fields differ:
    "ancestor_information_content" is semsimian's name for the Resnik measure.)"""

    detail_key: str  # which per-pair score to read out of an _all_pairs_detail() dict
    sql_rank: str  # SQL expression over the `scored` CTE's resnik/jaccard columns to rank by


# accepted semsimian metric name -> how to score it
_METRICS = {
    "ancestor_information_content": _Metric(detail_key="resnik", sql_rank="resnik"),
    "jaccard_similarity": _Metric(detail_key="jaccard", sql_rank="jaccard"),
    "phenodigm_score": _Metric(detail_key="phenodigm", sql_rank="sqrt(resnik * jaccard)"),
}


def _quote_list(values) -> str:
    return ",".join("'" + str(v).replace("'", "''") + "'" for v in values)


def _dedupe(seq):
    return list(dict.fromkeys(seq))  # preserve order, drop duplicates


class Ducksim:
    """Semantic-similarity engine over `monarch-kg.duckdb` (closure + edges), computed in DuckDB."""

    # entity->phenotype associations for search, from the KG `edges` table.
    #
    # Selected by PREDICATE rather than by association category, so every kind of phenotype-bearing
    # entity is searchable and the caller decides what to include via explicit category/taxon
    # filters. The previous category allowlist (gene + disease only) structurally hid the 589,030
    # GenotypeToPhenotypicFeature edges -- every MGI and MMRRC mouse model -- along with variants
    # and cases, with no way for a caller to opt in.
    #
    # Because the pool is now heterogeneous, an unfiltered search mixes categories. Callers that
    # mean "mouse genes" must say so (category=Gene, taxon=NCBITaxon:10090); a bare prefix no
    # longer implies a category. `SemsimSearchGroup` expands to exactly that, so the legacy API
    # keeps its old meaning.
    DEFAULT_ASSOCIATIONS = (
        "SELECT subject AS entity, object AS phenotype FROM src.edges "
        "WHERE predicate = 'biolink:has_phenotype' "
        # keep everything that isn't explicitly negated. `negated` is a VARCHAR today ('True'/'False'/
        # NULL), but try_cast-to-BOOLEAN keeps this correct across casing and a future boolean column;
        # NULL (and any unparseable value) coalesces to false so the row is kept, never silently dropped.
        "AND NOT coalesce(try_cast(negated AS BOOLEAN), false)"
    )

    def __init__(self, con: duckdb.DuckDBPyConnection):
        self.con = con

    def _read(self, sql, params=None):
        """Run a read query on a fresh cursor off the shared connection. The endpoints are sync, so
        FastAPI runs them in a threadpool; cursors from the same connection still serialize on the
        connection's internal lock (so intra-worker queries don't truly run in parallel), but a
        cursor per call keeps concurrent calls from clobbering each other's result state. Real
        parallelism comes from each uvicorn/gunicorn worker holding its own connection. Cursors
        share the same DuckDB instance, so they see the attached `src` db and the
        `_clo`/`_ic`/`_assoc`/`_esize` objects."""
        cur = self.con.cursor()
        return cur.execute(sql, params) if params is not None else cur.execute(sql)

    @classmethod
    def from_duckdb(
        cls,
        path,
        *,
        closure_table="closure",
        subject_col="subject_id",
        predicate_col="predicate_id",
        object_col="object_id",
        predicates=DEFAULT_PREDICATES,
        associations="default",
        memory_limit="2GB",
        threads=2,
    ):
        """Attach `path` read-only and define the closure/IC/association views over it.

        Read-only attach is what lets many workers share the OS page cache instead of each holding
        the ontology resident; `memory_limit` caps each worker's buffer pool. The attached db must
        carry koza's `information_content` / `closure_size` precompute tables (see module docstring).
        """
        con = duckdb.connect()
        # Single-quote-escape values interpolated into SQL (path comes from the
        # MONARCH_KG_DUCKDB_PATH env var; a quote in it would otherwise break the SQL).
        safe_mem = memory_limit.replace("'", "''")
        safe_path = str(path).replace("'", "''")
        con.execute(f"SET memory_limit = '{safe_mem}'")
        con.execute(f"SET threads = {int(threads)}")
        con.execute(f"ATTACH '{safe_path}' AS src (READ_ONLY)")
        self = cls(con)
        self._define_closure(
            f"SELECT {subject_col} AS s, {predicate_col} AS p, {object_col} AS o FROM src.{closure_table}", predicates
        )
        if associations is not None:
            self._define_associations(cls.DEFAULT_ASSOCIATIONS if associations == "default" else associations)
        return self

    # ---- setup ----------------------------------------------------------

    def _baked(self, name):
        """True if the attached source carries the named precompute table."""
        try:
            return (
                self.con.execute(
                    "SELECT count(*) FROM duckdb_tables() WHERE database_name = 'src' AND table_name = ?", [name]
                ).fetchone()[0]
                > 0
            )
        except duckdb.Error:
            return False

    def _require_baked(self, name):
        """ducksim reads koza's precompute tables; it does not recompute them. Fail loud (rather than
        silently rebuild, which would risk diverging from koza's definition) if one is missing."""
        if not self._baked(name):
            raise RuntimeError(
                f"attached monarch-kg.duckdb is missing the '{name}' table; run koza's "
                f"`information-content` operation (monarch-ingest) before using ducksim"
            )

    def _define_closure(self, source_sql, predicates):
        preds = _quote_list(predicates)
        # _clo: koza's precomputed (reflexive, transitive) closure, filtered to the chosen predicate
        # and projected to (s, o) = (term, ancestor). A view, so the big table stays in the shared
        # read-only source rather than being copied per worker.
        self.con.execute(f"CREATE VIEW _clo AS SELECT s, o FROM ({source_sql}) WHERE p IN ({preds})")
        self._require_baked("information_content")
        self.con.execute("CREATE VIEW _ic AS SELECT term, ic FROM src.information_content")
        self.has_search = False

    def _define_associations(self, assoc_sql):
        self.con.execute(f"CREATE VIEW _assoc AS {assoc_sql}")
        self._require_baked("closure_size")
        self.con.execute("CREATE VIEW _esize AS SELECT entity, size AS pn FROM src.closure_size")
        self._define_entity_metadata()
        self.has_search = True

    def _define_entity_metadata(self):
        """`_emeta`: (entity, category, taxon) for every searchable entity — what explicit
        category/taxon filtering resolves against.

        Materialized rather than left as a view over `src.nodes`: it is small (one row per
        phenotype-annotated entity, ~200K) and every filtered search probes it, so paying the join
        once at startup beats re-joining a 1.58M-row table per query.

        A `nodes` table lacking `category`/`in_taxon` (minimal or older artifacts) is tolerated
        rather than fatal, but the missing dimension is recorded so `entity_filter` can refuse a
        filter it cannot honor. Filtering on an absent column would otherwise match nothing and
        look like a legitimately empty result — the same silent-empty failure `closure_size`
        already causes for genotypes in `_flat`.
        """
        cols = {
            r[0]
            for r in self.con.execute(
                "SELECT column_name FROM duckdb_columns() WHERE database_name = 'src' AND table_name = 'nodes'"
            ).fetchall()
        }
        self.entity_metadata = {d for d in ("category", "in_taxon") if d in cols}
        cat = "n.category" if "category" in cols else "CAST(NULL AS VARCHAR)"
        tax = "n.in_taxon" if "in_taxon" in cols else "CAST(NULL AS VARCHAR)"
        taxl = "n.in_taxon_label" if "in_taxon_label" in cols else "CAST(NULL AS VARCHAR)"
        self.con.execute(f"""
            CREATE OR REPLACE TABLE _emeta AS
            SELECT DISTINCT n.id AS entity, {cat} AS category,
                   {tax} AS taxon, {taxl} AS taxon_label
            FROM (SELECT DISTINCT entity FROM _assoc) a JOIN src.nodes n ON n.id = a.entity
        """)
        self.con.execute("CREATE INDEX IF NOT EXISTS _ix_emeta ON _emeta(entity)")

    # ---- explicit filtering ---------------------------------------------

    def entity_filter(self, *, prefixes=None, categories=None, taxa=None, entities=None) -> str:
        """Build the SQL WHERE clause selecting which entities a search may return.

        Every argument is an optional list and they AND together; passing none searches everything.
        This is the explicit replacement for the old single-`prefix` argument, which conflated
        category and taxon into a data-source proxy and so could express "Mouse Genes" but not
        "mouse models" (MGI and MMRRC genotypes live under two different prefixes) nor "any
        genotype in any species".

        `taxa` accepts either a CURIE ('NCBITaxon:10090') or a label ('Mus musculus'); labels are
        matched case-insensitively so callers need not know which form the KG stores.
        """
        for requested, dimension in ((categories, "category"), (taxa, "in_taxon")):
            if requested and dimension not in getattr(self, "entity_metadata", set()):
                raise RuntimeError(
                    f"cannot filter by {dimension}: the attached KG's `nodes` table has no "
                    f"'{dimension}' column, so this filter would match nothing"
                )
        clauses = []
        if entities:
            clauses.append(f"entity IN (SELECT unnest([{_quote_list(entities)}]::VARCHAR[]))")
        if prefixes:
            clauses.append(f"split_part(entity, ':', 1) IN ({_quote_list(prefixes)})")
        meta = []
        if categories:
            meta.append(f"category IN ({_quote_list(categories)})")
        if taxa:
            meta.append(f"(taxon IN ({_quote_list(taxa)}) OR lower(taxon_label) IN ({_quote_list(t.lower() for t in taxa)}))")
        if meta:
            clauses.append(f"entity IN (SELECT entity FROM _emeta WHERE {' AND '.join(meta)})")
        return f"WHERE {' AND '.join(clauses)}" if clauses else ""

    def categories(self) -> list:
        """Distinct (category, taxon, taxon_label, count) available to search — lets a caller (or
        an API docs page) discover valid filter values instead of guessing them."""
        return self._read(
            "SELECT category, taxon, taxon_label, count(*) AS n FROM _emeta "
            "GROUP BY 1, 2, 3 ORDER BY n DESC"
        ).fetchall()

    # ---- labels ---------------------------------------------------------

    def labels(self, ids) -> dict:
        """Term/entity id -> name, from the KG `nodes` table."""
        ids = [i for i in _dedupe(i for i in ids if i)]
        if not ids:
            return {}
        rows = self._read(
            f"SELECT id, name FROM src.nodes WHERE id IN (SELECT unnest([{_quote_list(ids)}]::VARCHAR[]))"
        ).fetchall()
        return {i: name for i, name in rows}

    def profile(self, entity_id) -> list:
        """The phenotype termset an entity is annotated with — its similarity query profile.

        Reads `_assoc`, so it is uniform across every entity type the association pool covers:
        a disease's HPO terms, a mouse genotype's MP terms, a phenopacket Case's HPO terms. That
        uniformity is the point — it lets one search primitive be driven by "this case", "this
        disease" or "this mouse" interchangeably, which is what patient->model and model->patient
        matching both need."""
        return self.entity_phenotypes_batch([entity_id]).get(entity_id, [])

    def entity_phenotypes_batch(self, entity_ids) -> dict:
        """{entity -> [phenotype, ...]} for many entities in one query — enriches a whole search page
        without a per-entity round-trip."""
        ids = _dedupe(e for e in entity_ids if e)
        if not ids:
            return {}
        # ORDER BY for a deterministic, reproducible best-match tie-break.
        rows = self._read(
            f"SELECT DISTINCT entity, phenotype FROM _assoc "
            f"WHERE entity IN (SELECT unnest([{_quote_list(ids)}]::VARCHAR[])) "
            f"ORDER BY entity, phenotype"
        ).fetchall()
        out = {}
        for e, p in rows:
            out.setdefault(e, []).append(p)
        return out

    def entities(self, entity_ids) -> dict:
        """{id -> column->value row dict} from the KG `nodes` table — all-DuckDB entity hydration of
        search results, so the similarity backend needs no external entity store. One query."""
        ids = _dedupe(e for e in entity_ids if e)
        if not ids:
            return {}
        cur = self._read(f"SELECT * FROM src.nodes WHERE id IN (SELECT unnest([{_quote_list(ids)}]::VARCHAR[]))")
        cols = [d[0] for d in cur.description]
        rows = (dict(zip(cols, row)) for row in cur.fetchall())
        return {r["id"]: r for r in rows}

    # ---- pairwise detail ------------------------------------------------

    def _all_pairs_detail(self, subjects, objects) -> dict:
        """For every (subject term × object term): jaccard, resnik, phenodigm, and the MICA
        (max-IC shared ancestor). One DuckDB query. Pairs with no shared ancestor are omitted."""
        subj_q, obj_q = _quote_list(subjects), _quote_list(objects)
        rows = self._read(f"""
            WITH s_terms(t) AS (SELECT unnest([{subj_q}]::VARCHAR[])),
                 o_terms(t) AS (SELECT unnest([{obj_q}]::VARCHAR[])),
                 allterms AS (SELECT t FROM s_terms UNION SELECT t FROM o_terms),
                 qanc AS (SELECT DISTINCT s AS t, o AS a FROM _clo WHERE s IN (SELECT t FROM allterms)),
                 sizes AS (SELECT t, count(*) AS sz FROM qanc GROUP BY t),
                 -- one row per shared ancestor of each (s, o) pair, carrying its IC
                 common AS (
                   SELECT s.t AS s, o.t AS o, sa.a AS a, _ic.ic AS ic
                   FROM s_terms s JOIN o_terms o ON true
                   JOIN qanc sa ON sa.t = s.t
                   JOIN qanc oa ON oa.t = o.t AND oa.a = sa.a
                   JOIN _ic ON _ic.term = sa.a
                 )
            SELECT c.s, c.o,
                   count(*) AS inter,            -- |shared ancestors|
                   max(c.ic) AS resnik,          -- Resnik = max IC over shared ancestors
                   arg_max(c.a, c.ic) AS mica,    -- the most-informative shared ancestor (MICA)
                   zs.sz AS sz_s, zo.sz AS sz_o
            FROM common c JOIN sizes zs ON zs.t = c.s JOIN sizes zo ON zo.t = c.o
            GROUP BY c.s, c.o, zs.sz, zo.sz
        """).fetchall()
        out = {}
        for s, o, inter, resnik, mica, sz_s, sz_o in rows:
            jaccard = inter / (sz_s + sz_o - inter)
            out[(s, o)] = {"jaccard": jaccard, "resnik": resnik, "phenodigm": (resnik * jaccard) ** 0.5, "mica": mica}
        return out

    def _similarity(self, s, o, d):
        """semsimian-style similarity map for a (subject, object) pair."""
        if d is None:
            return {
                "subject_id": s,
                "object_id": o,
                "jaccard_similarity": 0.0,
                "ancestor_information_content": 0.0,
                "phenodigm_score": 0.0,
                "ancestor_id": None,
            }
        return {
            "subject_id": s,
            "object_id": o,
            "jaccard_similarity": d["jaccard"],
            "ancestor_information_content": d["resnik"],
            "phenodigm_score": d["phenodigm"],
            "ancestor_id": d["mica"],
        }

    def _best_matches(self, sources, targets, pairs, metric_key, *, swapped):
        """For each source term, its best-matching target term (by metric_key) + similarity detail.
        `swapped` reverses the (s,o) key lookup when sources are the object terms."""
        result = {}
        for src in sources:
            best_t, best_d, best_score = None, None, -1.0
            for tgt in targets:
                key = (tgt, src) if swapped else (src, tgt)
                d = pairs.get(key)
                score = d[metric_key] if d else 0.0
                if score > best_score:
                    best_score, best_t, best_d = score, tgt, d
            if best_score < 0.0:  # no targets at all — no match, score floors at 0
                best_score = 0.0
            s_id, o_id = (best_t, src) if swapped else (src, best_t)
            result[src] = {
                "match_target": best_t,
                "score": best_score,
                "match_subsumer": best_d["mica"] if best_d else None,
                "similarity": self._similarity(s_id, o_id, best_d),
            }
        return result

    def termset_pairwise_similarity(
        self, subjects, objects, metric="ancestor_information_content", direction="bidirectional"
    ) -> dict:
        """Full pairwise-similarity result (matches semsimian's TermSetPairwiseSimilarity shape):
        per-term best matches with subsumer + similarity detail, the average_score, and best_score.
        Labels are filled in by the caller/service via `labels()`.

        `direction` selects how the per-term best matches collapse into average_score, so it lines up
        with the search ranking: subject_to_object = mean over subject terms, object_to_subject =
        mean over object terms, bidirectional = mean of the two."""
        spec = _METRICS.get(metric.lower())
        if spec is None:
            raise ValueError(f"unknown metric {metric!r}")
        subj, obj = _dedupe(subjects), _dedupe(objects)
        pairs = self._all_pairs_detail(subj, obj)
        return self._shape_comparison(subj, obj, pairs, spec.detail_key, metric, direction)

    def _shape_comparison(self, subj, obj, pairs, detail_key, metric, direction) -> dict:
        """Collapse a prefetched (subject×object) `pairs` detail map into the
        TermSetPairwiseSimilarity shape. Split out from `termset_pairwise_similarity` so search can
        compute `pairs` once for an entire result page (one DuckDB query) and shape every entity from
        it in memory — no per-entity round-trips. `subj`/`obj` must be pre-deduped, `detail_key` the
        per-pair score to rank by; `pairs` may cover more terms than this one entity (extra keys are
        ignored)."""
        subject_bm = self._best_matches(subj, obj, pairs, detail_key, swapped=False)
        object_bm = self._best_matches(obj, subj, pairs, detail_key, swapped=True)
        s_scores = [bm["score"] for bm in subject_bm.values()]
        o_scores = [bm["score"] for bm in object_bm.values()]
        s_avg = mean(s_scores) if s_scores else 0.0
        o_avg = mean(o_scores) if o_scores else 0.0
        average_by_direction = {
            "subject_to_object": s_avg,
            "object_to_subject": o_avg,
            "bidirectional": (s_avg + o_avg) / 2 if s_scores and o_scores else 0.0,
        }
        if direction not in average_by_direction:
            raise ValueError(f"unknown direction {direction!r}")
        average_score = average_by_direction[direction]
        best_score = max(s_scores + o_scores, default=0.0)
        return {
            "metric": metric,
            "average_score": average_score,
            "best_score": best_score,
            "subject_termset": subj,
            "object_termset": obj,
            "subject_best_matches": subject_bm,
            "object_best_matches": object_bm,
        }

    # ---- search ---------------------------------------------------------

    def _termset_search(self, query_terms, metric, entity_filter, limit, direction="bidirectional"):
        """Score entities passing `entity_filter` by termset best-match-average — one DuckDB query.
        Shared by full_search (filter = prefix) and hybrid_search (Flat candidates). `direction`:
        the entity is the subject, so subject_to_object = entity->query (dir1), object_to_subject =
        query->entity (dir2), bidirectional = mean."""
        if not self.has_search:
            raise RuntimeError("search needs associations; pass associations= to from_duckdb")
        spec = _METRICS.get(metric.lower())
        if spec is None:
            raise ValueError(f"unknown metric {metric!r}")
        score_combiner = {
            "subject_to_object": "coalesce(d1.avg1, 0)",
            "object_to_subject": "coalesce(d2.avg2, 0)",
            "bidirectional": "(coalesce(d1.avg1, 0) + coalesce(d2.avg2, 0)) / 2.0",
        }.get(direction)
        if score_combiner is None:
            raise ValueError(f"unknown direction {direction!r}")
        self._require_phenotype_tables()
        Q = _quote_list(set(query_terms))
        score_expr = spec.sql_rank
        lim = "" if limit is None else f"LIMIT {int(limit)}"
        sql = f"""
        WITH qterms(q) AS (SELECT unnest([{Q}]::VARCHAR[])),
             q_anc AS (SELECT qt.q AS q, c.o AS a, ic.ic AS ic
                       FROM qterms qt JOIN _clo c ON c.s = qt.q JOIN _ic ic ON ic.term = c.o),
             qsize AS (SELECT q, count(*) AS sz FROM q_anc GROUP BY q),
             nq AS (SELECT count(*) AS n FROM qterms),
             -- Scoring happens at the PHENOTYPE level, not per (entity, phenotype). A phenotype's
             -- similarity to a query term does not depend on which entity carries it, so expanding
             -- ancestors per association row recomputes the same ancestor set once per annotated
             -- entity. Across mouse genotypes that is 447,110 rows covering 11,530 distinct MP
             -- terms -- ~39x redundant, and the dominant cost of the whole query.
             pair AS (SELECT pa.p, qa.q, count(*) AS inter, max(qa.ic) AS resnik
                      FROM _ph_anc pa JOIN q_anc qa ON qa.a = pa.a GROUP BY pa.p, qa.q),
             ranked AS (SELECT s.p, s.q, {score_expr} AS score FROM
                        (SELECT pr.p, pr.q, pr.resnik,
                                pr.inter::DOUBLE / (ps.sz + qs.sz - pr.inter) AS jaccard
                         FROM pair pr JOIN _psize ps ON ps.p = pr.p
                                      JOIN qsize qs ON qs.q = pr.q) s),
             -- entities enter only here, by joining the per-phenotype scores onto their annotations
             ent_ph AS (SELECT entity AS e, phenotype AS p FROM _ent_ph {entity_filter}),
             dir1 AS (SELECT ep.e, sum(bp.best) / any_value(np.n) AS avg1
                      FROM ent_ph ep
                      JOIN (SELECT p, max(score) AS best FROM ranked GROUP BY p) bp ON bp.p = ep.p
                      JOIN _np np ON np.e = ep.e GROUP BY ep.e),
             dir2 AS (SELECT e, sum(best) / (SELECT n FROM nq) AS avg2 FROM
                      (SELECT ep.e, r.q, max(r.score) AS best
                       FROM ent_ph ep JOIN ranked r ON r.p = ep.p GROUP BY ep.e, r.q) GROUP BY e)
        SELECT coalesce(d1.e, d2.e) AS entity, {score_combiner} AS score
        FROM dir1 d1 FULL OUTER JOIN dir2 d2 ON d1.e = d2.e
        ORDER BY score DESC, entity {lim}
        """
        return self._read(sql).fetchall()

    def _require_phenotype_tables(self):
        """Materialize the phenotype-level tables `_termset_search` scores against. Built once on
        first search (a few seconds), reused by every later query.

        `_ent_ph` is deduped here because an entity may be annotated to the same phenotype through
        several association rows (different evidence or sources). Left undeduped, an entity's
        matched phenotype would be counted once per row and `dir1` would over-sum. `_np` is derived
        from the same deduped table so the two necessarily agree.
        """
        if getattr(self, "_pheno_ready", False):
            return
        self.con.execute("CREATE OR REPLACE TABLE _ent_ph AS SELECT DISTINCT entity, phenotype FROM _assoc")
        self.con.execute("CREATE OR REPLACE TABLE _np AS SELECT entity AS e, count(*) AS n FROM _ent_ph GROUP BY 1")
        self.con.execute("""
            CREATE OR REPLACE TABLE _ph_anc AS
            SELECT DISTINCT ep.phenotype AS p, c.o AS a
            FROM (SELECT DISTINCT phenotype FROM _ent_ph) ep JOIN _clo c ON c.s = ep.phenotype
        """)
        self.con.execute("CREATE OR REPLACE TABLE _psize AS SELECT p, count(*) AS sz FROM _ph_anc GROUP BY p")
        self.con.execute("CREATE INDEX IF NOT EXISTS _ix_ph_anc_a ON _ph_anc(a)")
        self.con.execute("CREATE INDEX IF NOT EXISTS _ix_ent_ph_p ON _ent_ph(phenotype)")
        self._pheno_ready = True

    def full_search(
        self,
        query_terms,
        *,
        limit=10,
        metric="ancestor_information_content",
        prefix=None,
        direction="bidirectional",
        categories=None,
        taxa=None,
        prefixes=None,
    ):
        """Score every entity passing the filters by the termset best-match-average — one DuckDB
        query. Matches semsimian's Full mode; more accurate than Hybrid (no Jaccard prefilter
        dropping true-top entities).

        `categories`/`taxa`/`prefixes` are the explicit filters and AND together. `prefix` is the
        legacy single-value form, kept working for existing callers.
        """
        ef = self.entity_filter(
            prefixes=prefixes or ([prefix] if prefix else None), categories=categories, taxa=taxa
        )
        return self._termset_search(query_terms, metric, ef, limit, direction)

    def hybrid_search(
        self,
        query_terms,
        *,
        limit=10,
        metric="ancestor_information_content",
        prefix=None,
        direction="bidirectional",
        categories=None,
        taxa=None,
        prefixes=None,
    ):
        """Hybrid search — semsimian's production mode: cheap Jaccard prefilter then termset rerank,
        as one query over the candidate set. (The Jaccard prefilter is direction-agnostic; the
        rerank honors `direction`.)"""
        ef = self.entity_filter(
            prefixes=prefixes or ([prefix] if prefix else None), categories=categories, taxa=taxa
        )
        flat = self._flat(query_terms, ef)
        if not flat:
            return []
        scores = sorted({j for _, j in flat}, reverse=True)
        k = max(math.ceil((limit / 1000.0) * len(scores)), limit)
        cutoff = scores[k] if k < len(scores) else scores[-1]
        candidates = [e for e, j in flat if j >= cutoff]
        return self._termset_search(
            query_terms, metric, self.entity_filter(entities=candidates), limit, direction
        )

    def _flat(self, query_terms, entity_filter=""):
        """Cheap set-Jaccard ranking of the filtered entities vs the query — Hybrid's candidate gen.

        `_esize` is koza's baked `closure_size`. It once covered only genes and diseases, so a
        plain inner join dropped every genotype silently and returned an empty candidate set with
        no error. koza now bakes a size for every entity carrying a has_phenotype edge
        (monarch-initiative/koza `fix(information-content)`), which covers all 213,273 of them.

        The LEFT JOIN and computed fallback stay as a compatibility shim: artifacts built before
        that fix are still in circulation, and degrading to a slower correct answer is better than
        silently returning none. Against a current artifact the fallback matches nothing and costs
        nothing.
        """
        Q = _quote_list(set(query_terms))
        self._require_phenotype_tables()
        return self._read(f"""
            WITH qt(t) AS (SELECT unnest([{Q}]::VARCHAR[])),
                 q_anc AS (SELECT DISTINCT c.o AS a FROM _clo c JOIN qt ON c.s = qt.t),
                 qn AS (SELECT count(*) AS n FROM q_anc),
                 ent AS (SELECT entity, phenotype FROM _ent_ph {entity_filter}),
                 inter AS (SELECT a.entity, count(DISTINCT c.o) AS inter
                           FROM ent a JOIN _clo c ON c.s = a.phenotype JOIN q_anc q ON q.a = c.o
                           GROUP BY a.entity),
                 -- baked sizes where present, computed for the entities koza did not precompute
                 sz AS (SELECT i.entity, coalesce(e.pn, f.pn) AS pn
                        FROM inter i
                        LEFT JOIN _esize e ON e.entity = i.entity
                        LEFT JOIN (SELECT ep.entity, count(DISTINCT pa.a) AS pn
                                   FROM ent ep JOIN _ph_anc pa ON pa.p = ep.phenotype
                                   GROUP BY ep.entity) f ON f.entity = i.entity)
            SELECT i.entity, i.inter::DOUBLE / ((SELECT n FROM qn) + sz.pn - i.inter) AS jaccard
            FROM inter i JOIN sz ON sz.entity = i.entity
            ORDER BY jaccard DESC, i.entity
        """).fetchall()

    # ---- search with full per-result detail -----------------------------

    def search(
        self,
        query_terms,
        *,
        limit=10,
        metric="ancestor_information_content",
        prefix=None,
        direction="bidirectional",
        mode="hybrid",
        categories=None,
        taxa=None,
        prefixes=None,
    ):
        """All-DuckDB search: rank entities (Hybrid by default; Full when `mode="full"`), then enrich
        the whole page with full termset detail in a constant number of queries — independent of
        `limit`, no per-result round-trips. Returns [(entity_id, score, comparison)] where
        `comparison` matches `termset_pairwise_similarity`'s shape (the entity's phenotypes are the
        subjects, the query terms the objects — so `comparison["average_score"]` equals `score`).
        Labels and entity hydration are added by the caller (also batched)."""
        spec = _METRICS.get(metric.lower())
        if spec is None:
            raise ValueError(f"unknown metric {metric!r}")
        ranker = self.full_search if mode == "full" else self.hybrid_search
        ranked = ranker(
            query_terms,
            limit=limit,
            metric=metric,
            prefix=prefix,
            direction=direction,
            categories=categories,
            taxa=taxa,
            prefixes=prefixes,
        )
        if not ranked:
            return []
        entity_ids = [e for e, _ in ranked]
        pheno_by_entity = self.entity_phenotypes_batch(entity_ids)
        obj = _dedupe(query_terms)
        # every phenotype across the page, scored against the query once (single DuckDB query); each
        # entity then reuses the relevant slice of this `pairs` map when shaped below.
        all_phenos = _dedupe(p for e in entity_ids for p in pheno_by_entity.get(e, []))
        pairs = self._all_pairs_detail(all_phenos, obj)
        out = []
        for entity_id, score in ranked:
            subj = _dedupe(pheno_by_entity.get(entity_id, []))
            comparison = self._shape_comparison(subj, obj, pairs, spec.detail_key, metric, direction)
            out.append((entity_id, score, comparison))
        return out
