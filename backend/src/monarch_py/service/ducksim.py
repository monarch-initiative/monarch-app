"""ducksim — semantic similarity (semsimian-equivalent) computed in DuckDB.

Reads the ontology closure + KG edges directly from the read-only `monarch-kg.duckdb` artifact the
api already ships at /data, so there's no separate in-memory service holding the ontology resident.
Validated bit-exact against semsimian's committed test values and to FP precision against the live
library at scale (see the ducksim workspace; this is the production-only port — the equivalence
harness and the SQLite/phenio test backend live there, not here).

Metric definitions:  IC(t) = -log2(freq/N) (freq = #closure triples with t as object, N = #distinct
objects); closure is reflexive; Jaccard = |anc(a)∩anc(b)| / |anc(a)∪anc(b)|; Resnik = max IC over
shared ancestors; Phenodigm = sqrt(Resnik·Jaccard); termset score = bidirectional best-match-average.
"""

from __future__ import annotations

import math
from statistics import mean

import duckdb

DEFAULT_PREDICATES = ("rdfs:subClassOf",)

# public metric names (semsimian's) -> internal detail key
_METRIC_ALIASES = {
    "ancestor_information_content": "resnik", "resnik": "resnik", "ic": "resnik",
    "jaccard_similarity": "jaccard", "jaccard": "jaccard",
    "phenodigm_score": "phenodigm", "phenodigm": "phenodigm",
}


def _quote_list(values) -> str:
    return ",".join("'" + str(v).replace("'", "''") + "'" for v in values)


def _dedupe(seq):
    return list(dict.fromkeys(seq))  # preserve order, drop duplicates


class Ducksim:
    """Semantic-similarity engine over `monarch-kg.duckdb` (closure + edges), computed in DuckDB."""

    # entity->phenotype associations for search, from the KG `edges` table
    DEFAULT_ASSOCIATIONS = (
        "SELECT subject AS entity, object AS phenotype FROM src.edges "
        "WHERE category IN ('biolink:GeneToPhenotypicFeatureAssociation',"
        "'biolink:DiseaseToPhenotypicFeatureAssociation') "
        "AND predicate = 'biolink:has_phenotype' AND (negated IS NULL OR negated = 'False')"
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
    def from_duckdb(cls, path, *, closure_table="closure", subject_col="subject_id",
                    predicate_col="predicate_id", object_col="object_id",
                    predicates=DEFAULT_PREDICATES, associations="default", memory_limit="2GB",
                    threads=2):
        """Attach `path` read-only and build the IC table + closure/association views.

        Read-only attach is what lets many workers share the OS page cache instead of each holding
        the ontology resident; `memory_limit` caps each worker's buffer pool.
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
            f"SELECT {subject_col} AS s, {predicate_col} AS p, {object_col} AS o "
            f"FROM src.{closure_table}", predicates)
        if associations is not None:
            self._define_associations(cls.DEFAULT_ASSOCIATIONS if associations == "default"
                                      else associations)
        return self

    # ---- setup ----------------------------------------------------------

    def _baked(self, name):
        """True if the attached source carries a pre-built precompute table — so we skip the runtime
        build and just read it (shared via the OS page cache). Built by koza's `information-content`
        operation during the KG build (monarch-ingest)."""
        try:
            return self.con.execute(
                "SELECT count(*) FROM duckdb_tables() WHERE database_name = 'src' AND table_name = ?",
                [name]).fetchone()[0] > 0
        except Exception:
            return False

    def _define_closure(self, source_sql, predicates):
        preds = _quote_list(predicates)
        self.con.execute(f"CREATE VIEW _clo AS SELECT s, o FROM ({source_sql}) WHERE p IN ({preds})")
        if self._baked("information_content"):
            self.con.execute("CREATE VIEW _ic AS SELECT term, ic FROM src.information_content")
        else:
            self.con.execute("""
                CREATE TABLE _ic AS
                WITH n AS (SELECT count(DISTINCT o) AS nn FROM _clo)
                SELECT o AS term, -log2(count(*)::DOUBLE / (SELECT nn FROM n)) AS ic
                FROM _clo GROUP BY o
            """)
        self.has_search = False

    def _define_associations(self, assoc_sql):
        self.con.execute(f"CREATE VIEW _assoc AS {assoc_sql}")
        if self._baked("closure_size"):
            self.con.execute(
                "CREATE VIEW _esize AS SELECT entity, size AS pn FROM src.closure_size"
            )
        else:
            self.con.execute("""
                CREATE TABLE _esize AS
                SELECT a.entity, count(DISTINCT c.o) AS pn
                FROM _assoc a JOIN _clo c ON c.s = a.phenotype GROUP BY a.entity
            """)
        self.has_search = True

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

    def entity_phenotypes(self, entity_id) -> list:
        """The phenotype terms associated with an entity (for reranking / per-result similarity)."""
        return [r[0] for r in self._read(
            "SELECT DISTINCT phenotype FROM _assoc WHERE entity = ?", [entity_id]).fetchall()]

    def entity_phenotypes_batch(self, entity_ids) -> dict:
        """{entity -> [phenotype, ...]} for many entities in one query. Lets a whole search page be
        enriched without a per-entity round-trip (the batched form of `entity_phenotypes`)."""
        ids = _dedupe(e for e in entity_ids if e)
        if not ids:
            return {}
        # ORDER BY for a deterministic, reproducible best-match tie-break (the per-entity
        # `entity_phenotypes` left phenotype order unspecified, so ties resolved arbitrarily).
        rows = self._read(
            f"SELECT DISTINCT entity, phenotype FROM _assoc "
            f"WHERE entity IN (SELECT unnest([{_quote_list(ids)}]::VARCHAR[])) "
            f"ORDER BY entity, phenotype").fetchall()
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
        cur = self._read(
            f"SELECT * FROM src.nodes "
            f"WHERE id IN (SELECT unnest([{_quote_list(ids)}]::VARCHAR[]))")
        cols = [d[0] for d in cur.description]
        rows = (dict(zip(cols, row)) for row in cur.fetchall())
        return {r["id"]: r for r in rows}

    # ---- pairwise detail ------------------------------------------------

    def _all_pairs_detail(self, subjects, objects) -> dict:
        """For every (subject term × object term): jaccard, resnik, phenodigm, and the MICA
        (max-IC shared ancestor). One DuckDB query. Pairs with no shared ancestor are omitted."""
        S, O = _quote_list(subjects), _quote_list(objects)
        rows = self._read(f"""
            WITH s_terms(t) AS (SELECT unnest([{S}]::VARCHAR[])),
                 o_terms(t) AS (SELECT unnest([{O}]::VARCHAR[])),
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
            out[(s, o)] = {"jaccard": jaccard, "resnik": resnik,
                           "phenodigm": (resnik * jaccard) ** 0.5, "mica": mica}
        return out

    def _similarity(self, s, o, d):
        """semsimian-style similarity map for a (subject, object) pair."""
        if d is None:
            return {"subject_id": s, "object_id": o, "jaccard_similarity": 0.0,
                    "ancestor_information_content": 0.0, "phenodigm_score": 0.0, "ancestor_id": None}
        return {"subject_id": s, "object_id": o, "jaccard_similarity": d["jaccard"],
                "ancestor_information_content": d["resnik"], "phenodigm_score": d["phenodigm"],
                "ancestor_id": d["mica"]}

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
            result[src] = {"match_target": best_t, "score": best_score,
                           "match_subsumer": best_d["mica"] if best_d else None,
                           "similarity": self._similarity(s_id, o_id, best_d)}
        return result

    def termset_pairwise_similarity(self, subjects, objects,
                                    metric="ancestor_information_content",
                                    direction="bidirectional") -> dict:
        """Full pairwise-similarity result (matches semsimian's TermSetPairwiseSimilarity shape):
        per-term best matches with subsumer + similarity detail, the average_score, and best_score.
        Labels are filled in by the caller/service via `labels()`.

        `direction` selects how the per-term best matches collapse into average_score, so it lines up
        with the search ranking: subject_to_object = mean over subject terms, object_to_subject =
        mean over object terms, bidirectional = mean of the two."""
        mk = _METRIC_ALIASES.get(metric.lower())
        if mk is None:
            raise ValueError(f"unknown metric {metric!r}")
        subj, obj = _dedupe(subjects), _dedupe(objects)
        pairs = self._all_pairs_detail(subj, obj)
        return self._shape_comparison(subj, obj, pairs, mk, metric, direction)

    def _shape_comparison(self, subj, obj, pairs, mk, metric, direction) -> dict:
        """Collapse a prefetched (subject×object) `pairs` detail map into the
        TermSetPairwiseSimilarity shape. Split out from `termset_pairwise_similarity` so search can
        compute `pairs` once for an entire result page (one DuckDB query) and shape every entity from
        it in memory — no per-entity round-trips. `subj`/`obj` must be pre-deduped, `mk` a resolved
        metric key; `pairs` may cover more terms than this one entity (extra keys are ignored)."""
        subject_bm = self._best_matches(subj, obj, pairs, mk, swapped=False)
        object_bm = self._best_matches(obj, subj, pairs, mk, swapped=True)
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
        return {"metric": metric, "average_score": average_score, "best_score": best_score,
                "subject_termset": subj, "object_termset": obj,
                "subject_best_matches": subject_bm, "object_best_matches": object_bm}

    # ---- search ---------------------------------------------------------

    def _termset_search(self, query_terms, metric, entity_filter, limit, direction="bidirectional"):
        """Score entities passing `entity_filter` by termset best-match-average — one DuckDB query.
        Shared by full_search (filter = prefix) and hybrid_search (Flat candidates). `direction`:
        the entity is the subject, so subject_to_object = entity->query (dir1), object_to_subject =
        query->entity (dir2), bidirectional = mean."""
        if not self.has_search:
            raise RuntimeError("search needs associations; pass associations= to from_duckdb")
        mk = _METRIC_ALIASES.get(metric.lower())
        if mk is None:
            raise ValueError(f"unknown metric {metric!r}")
        score_combiner = {
            "subject_to_object": "coalesce(d1.avg1, 0)",
            "object_to_subject": "coalesce(d2.avg2, 0)",
            "bidirectional": "(coalesce(d1.avg1, 0) + coalesce(d2.avg2, 0)) / 2.0",
        }.get(direction)
        if score_combiner is None:
            raise ValueError(f"unknown direction {direction!r}")
        Q = _quote_list(set(query_terms))
        score_expr = {"resnik": "resnik", "jaccard": "jaccard",
                      "phenodigm": "sqrt(resnik * jaccard)"}[mk]
        lim = "" if limit is None else f"LIMIT {int(limit)}"
        sql = f"""
        WITH qterms(q) AS (SELECT unnest([{Q}]::VARCHAR[])),
             q_anc AS (SELECT qt.q AS q, c.o AS a, ic.ic AS ic
                       FROM qterms qt JOIN _clo c ON c.s = qt.q JOIN _ic ic ON ic.term = c.o),
             qsize AS (SELECT q, count(*) AS sz FROM q_anc GROUP BY q),
             nq AS (SELECT count(*) AS n FROM qterms),
             ent_ph AS (SELECT entity AS e, phenotype AS p FROM _assoc {entity_filter}),
             np AS (SELECT e, count(DISTINCT p) AS n FROM ent_ph GROUP BY e),
             p_anc AS (SELECT ep.e, ep.p, c.o AS a FROM ent_ph ep JOIN _clo c ON c.s = ep.p),
             psize AS (SELECT e, p, count(DISTINCT a) AS sz FROM p_anc GROUP BY e, p),
             pair AS (
               SELECT pa.e, pa.p, qa.q, count(*) AS inter, max(qa.ic) AS resnik
               FROM p_anc pa JOIN q_anc qa ON qa.a = pa.a GROUP BY pa.e, pa.p, qa.q
             ),
             scored AS (
               SELECT pr.e, pr.p, pr.q, pr.resnik,
                      pr.inter::DOUBLE / (ps.sz + qs.sz - pr.inter) AS jaccard
               FROM pair pr JOIN psize ps ON ps.e = pr.e AND ps.p = pr.p
                            JOIN qsize qs ON qs.q = pr.q
             ),
             ranked AS (SELECT e, p, q, {score_expr} AS score FROM scored),
             dir1 AS (SELECT bm.e, sum(bm.best) / np.n AS avg1
                      FROM (SELECT e, p, max(score) AS best FROM ranked GROUP BY e, p) bm
                      JOIN np ON np.e = bm.e GROUP BY bm.e, np.n),
             dir2 AS (SELECT bm.e, sum(bm.best) / (SELECT n FROM nq) AS avg2
                      FROM (SELECT e, q, max(score) AS best FROM ranked GROUP BY e, q) bm
                      GROUP BY bm.e)
        SELECT coalesce(d1.e, d2.e) AS entity, {score_combiner} AS score
        FROM dir1 d1 FULL OUTER JOIN dir2 d2 ON d1.e = d2.e
        ORDER BY score DESC, entity {lim}
        """
        return self._read(sql).fetchall()

    def full_search(self, query_terms, *, limit=10, metric="ancestor_information_content",
                    prefix=None, direction="bidirectional"):
        """Score every entity (optionally restricted to CURIE `prefix`) by the termset
        best-match-average — one DuckDB query. Matches semsimian's Full mode; more accurate than
        Hybrid (no Jaccard prefilter dropping true-top entities)."""
        ef = f"WHERE split_part(entity, ':', 1) = {_quote_list([prefix])}" if prefix else ""
        return self._termset_search(query_terms, metric, ef, limit, direction)

    def hybrid_search(self, query_terms, *, limit=10, metric="ancestor_information_content",
                      prefix=None, direction="bidirectional"):
        """Hybrid search — semsimian's production mode: cheap Jaccard prefilter then termset rerank,
        as one query over the candidate set. (The Jaccard prefilter is direction-agnostic; the
        rerank honors `direction`.)"""
        flat = self._flat(query_terms, prefix)
        if not flat:
            return []
        scores = sorted({j for _, j in flat}, reverse=True)
        k = max(math.ceil((limit / 1000.0) * len(scores)), limit)
        cutoff = scores[k] if k < len(scores) else scores[-1]
        candidates = [e for e, j in flat if j >= cutoff]
        ef = f"WHERE entity IN (SELECT unnest([{_quote_list(candidates)}]::VARCHAR[]))"
        return self._termset_search(query_terms, metric, ef, limit, direction)

    def _flat(self, query_terms, prefix):
        """Cheap set-Jaccard ranking of all (prefix) entities vs the query — Hybrid's candidate gen."""
        Q = _quote_list(set(query_terms))
        pfilter = f"AND split_part(i.entity, ':', 1) = {_quote_list([prefix])}" if prefix else ""
        return self._read(f"""
            WITH qt(t) AS (SELECT unnest([{Q}]::VARCHAR[])),
                 q_anc AS (SELECT DISTINCT c.o AS a FROM _clo c JOIN qt ON c.s = qt.t),
                 qn AS (SELECT count(*) AS n FROM q_anc),
                 inter AS (SELECT a.entity, count(DISTINCT c.o) AS inter
                           FROM _assoc a JOIN _clo c ON c.s = a.phenotype JOIN q_anc q ON q.a = c.o
                           GROUP BY a.entity)
            SELECT i.entity, i.inter::DOUBLE / ((SELECT n FROM qn) + e.pn - i.inter) AS jaccard
            FROM inter i JOIN _esize e ON e.entity = i.entity
            WHERE true {pfilter} ORDER BY jaccard DESC, i.entity
        """).fetchall()

    # ---- search with full per-result detail -----------------------------

    def search(self, query_terms, *, limit=10, metric="ancestor_information_content",
               prefix=None, direction="bidirectional", mode="hybrid"):
        """All-DuckDB search: rank entities (Hybrid by default; Full when `mode="full"`), then enrich
        the whole page with full termset detail in a constant number of queries — independent of
        `limit`, no per-result round-trips. Returns [(entity_id, score, comparison)] where
        `comparison` matches `termset_pairwise_similarity`'s shape (the entity's phenotypes are the
        subjects, the query terms the objects — so `comparison["average_score"]` equals `score`).
        Labels and entity hydration are added by the caller (also batched)."""
        mk = _METRIC_ALIASES.get(metric.lower())
        if mk is None:
            raise ValueError(f"unknown metric {metric!r}")
        ranker = self.full_search if mode == "full" else self.hybrid_search
        ranked = ranker(query_terms, limit=limit, metric=metric, prefix=prefix, direction=direction)
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
            comparison = self._shape_comparison(subj, obj, pairs, mk, metric, direction)
            out.append((entity_id, score, comparison))
        return out
