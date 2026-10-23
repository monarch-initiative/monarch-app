"""ducksim — semantic similarity (semsimian-equivalent) computed in DuckDB.

Reads the ontology closure + KG edges directly from the read-only `monarch-kg.duckdb` artifact the
api already ships at /data, so there's no separate in-memory service holding the ontology resident.
Validated bit-exact against semsimian's committed test values and to FP precision against the live
library at scale (see the ducksim workspace; this is the production-only port — the equivalence
harness and the SQLite/phenio test backend live there, not here).

ducksim is a pure reader of the precompute tables koza's `information-content` operation bakes into
the artifact during the KG build (monarch-ingest): `information_content` (term, ic) and
`closure_size` (entity, size). It does not recompute them — a db missing them fails loud.

Annotation IC (optional): monarch-ingest also bakes annotation-based IC for each annotation corpus
(koza's `annotation-information-content`: IC(t) = log2(N / n(t)), n(t) = distinct entities annotated
to t or a descendant, N = distinct annotated entities) into one table, `annotation_information_content`
(corpus, term, ic), and lists the corpora in `pheno_comparison_corpora`. ducksim exposes each corpus as
an IC view keyed by its subject prefix. These tables are optional: a KG without them serves ontology IC
as before, and a request for annotation IC gets `AnnotationICUnavailable`.

Metric definitions:  IC(t) = -log2(freq/N) (freq = #closure triples with t as object, N = #distinct
objects); closure is reflexive; Jaccard = |anc(a)∩anc(b)| / |anc(a)∪anc(b)|; Resnik = max IC over
shared ancestors; Phenodigm = sqrt(Resnik·Jaccard); termset score = bidirectional best-match-average.
"""

from __future__ import annotations

import atexit
import errno
import math
import os
import re
import shutil
import tempfile
from pathlib import Path
from statistics import mean
from typing import NamedTuple

import duckdb

DEFAULT_PREDICATES = ("rdfs:subClassOf",)

# The annotation IC monarch-ingest bakes: one (corpus, term, ic) table, and the table listing its
# corpora (one row per corpus, with the subject prefixes of the entities it annotates).
ANNOTATION_IC_TABLE = "annotation_information_content"
ANNOTATION_IC_CORPUS_TABLE = "pheno_comparison_corpora"
ONTOLOGY_IC = "ontology"
ANNOTATION_IC = "annotation"
_SQL_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class AnnotationICUnavailable(LookupError):
    """Annotation IC was requested for a corpus the attached KG has no annotation IC for."""


# Tie-breaks for search ranking. "frequency" orders equal scores by how frequent the matched
# phenotypes are in each entity (see Ducksim._define_frequency).
NO_TIE_BREAK = "none"
FREQUENCY_TIE_BREAK = "frequency"
DEFAULT_FREQUENCY = 0.5
# Frequencies are floored here: some OMIM edges record 0 affected patients, and log(0) is undefined.
MIN_FREQUENCY = 0.01
# HPO frequency categories -> the midpoint of each category's range.
FREQUENCY_CATEGORY_MIDPOINTS = {
    "HP:0040280": 1.0,  # Obligate, 100%
    "HP:0040281": 0.9,  # Very frequent, 80-99%
    "HP:0040282": 0.55,  # Frequent, 30-79%
    "HP:0040283": 0.17,  # Occasional, 5-29%
    "HP:0040284": 0.025,  # Very rare, 1-4%
    "HP:0040285": 0.0,  # Excluded, 0% (floored to MIN_FREQUENCY)
}
# Score equality for the tie-break: entities whose scores are equal by construction (every query
# term matched exactly) can differ in the last bits from summation order.
_TIE_DECIMALS = 9


# DuckDB spills to `temp_directory` when a query exceeds `memory_limit`, which is expected
# under load. Its default is the *relative* path ".tmp", and its spill filenames are keyed by
# allocation-size class rather than by process — duckdb_temp_storage_S64K-0.tmp and friends.
# Every gunicorn worker shares a working directory, so without an explicit setting all of them
# write to the same handful of files and corrupt each other's spills the moment two spill at
# once. Give each process its own absolute directory instead.
_TEMP_ROOT_ENV = "DUCKSIM_TEMP_ROOT"
_WORKER_DIR_PREFIX = "worker-"
_WORKER_DIR_RE = re.compile(rf"^{_WORKER_DIR_PREFIX}(\d+)-")


def _process_alive(pid: int) -> bool:
    """Whether `pid` is still running. A live process we don't own raises EPERM, not ESRCH."""
    try:
        os.kill(pid, 0)
    except OSError as exc:
        return exc.errno == errno.EPERM
    return True


def _sweep_abandoned(root: Path) -> None:
    """Remove spill directories whose owning worker is gone.

    Workers are recycled frequently (gunicorn --max-requests), and atexit does not run on
    SIGKILL or OOM-kill, so cleanup cannot rely on the owner tidying up after itself. Sweeping
    on the way in keeps the root from accumulating a directory per recycled worker, and clears
    the orphaned spill files a previous crash left behind.
    """
    for child in root.iterdir():
        match = _WORKER_DIR_RE.match(child.name)
        if not match or not child.is_dir():
            continue
        if not _process_alive(int(match.group(1))):
            shutil.rmtree(child, ignore_errors=True)


def worker_temp_directory() -> str:
    """An absolute, per-process directory for DuckDB to spill into."""
    root = Path(os.getenv(_TEMP_ROOT_ENV) or Path(tempfile.gettempdir()) / "monarch-ducksim")
    root.mkdir(parents=True, exist_ok=True)
    try:
        _sweep_abandoned(root)
    except OSError:
        # Cleanup is best-effort: a sweep failure must not stop this worker from starting.
        pass
    # mkdtemp rather than a bare pid path, so a recycled worker that reuses a pid cannot land
    # on a directory the sweep has not reached yet. The pid stays in the name for the sweep.
    path = tempfile.mkdtemp(prefix=f"{_WORKER_DIR_PREFIX}{os.getpid()}-", dir=root)
    atexit.register(shutil.rmtree, path, True)
    return path


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

    # entity->phenotype associations for search, from the KG `edges` table
    DEFAULT_ASSOCIATIONS = (
        "SELECT subject AS entity, object AS phenotype FROM src.edges "
        "WHERE category IN ('biolink:GeneToPhenotypicFeatureAssociation',"
        "'biolink:DiseaseToPhenotypicFeatureAssociation') "
        "AND predicate = 'biolink:has_phenotype' "
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
        # Spills go to a directory owned by this process alone; see worker_temp_directory.
        safe_tmp = worker_temp_directory().replace("'", "''")
        con.execute(f"SET temp_directory = '{safe_tmp}'")
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
        self.annotation_ic_views = self._define_annotation_ic()
        self.has_search = False

    def _define_annotation_ic(self) -> dict:
        """{subject prefix -> IC view} for every annotation-IC corpus the KG lists. View definitions
        only: the IC is baked in the KG build, so nothing is computed here. Missing or malformed
        metadata leaves annotation IC unavailable rather than failing the worker."""
        if not self._baked(ANNOTATION_IC_CORPUS_TABLE) or not self._baked(ANNOTATION_IC_TABLE):
            return {}
        rows = self.con.execute(
            f"SELECT corpus, subject_prefixes FROM src.{ANNOTATION_IC_CORPUS_TABLE} "
            f"WHERE corpus IN (SELECT DISTINCT corpus FROM src.{ANNOTATION_IC_TABLE}) ORDER BY corpus"
        ).fetchall()
        views = {}
        for corpus, subject_prefixes in rows:
            if not corpus or not _SQL_IDENTIFIER.match(corpus):
                continue
            view = f"_ic_annotation_{corpus}"
            self.con.execute(
                f"CREATE VIEW {view} AS SELECT term, ic FROM src.{ANNOTATION_IC_TABLE} WHERE corpus = '{corpus}'"
            )
            for prefix in subject_prefixes or []:
                views.setdefault(prefix, view)
        return views

    def ic_view(self, information_content=ONTOLOGY_IC, prefix=None) -> str:
        """The IC view a request scores with. Annotation IC comes from the corpus whose annotated
        entities have CURIE prefix `prefix` (the search group, or the compare `group`)."""
        source = str(information_content or ONTOLOGY_IC).lower()
        if source == ONTOLOGY_IC:
            return "_ic"
        if source != ANNOTATION_IC:
            raise ValueError(f"unknown information_content {information_content!r}")
        if not prefix:
            raise AnnotationICUnavailable("annotation information content needs a group to choose its corpus")
        view = self.annotation_ic_views.get(prefix)
        if view is None:
            available = ", ".join(sorted(self.annotation_ic_views)) or "none"
            raise AnnotationICUnavailable(
                f"this KG has no annotation information content for {prefix} entities "
                f"(available: {available}). It is built by monarch-ingest; see #1475."
            )
        return view

    def _define_associations(self, assoc_sql):
        self.con.execute(f"CREATE VIEW _assoc AS {assoc_sql}")
        self._require_baked("closure_size")
        self.con.execute("CREATE VIEW _esize AS SELECT entity, size AS pn FROM src.closure_size")
        self._define_frequency()
        self.has_search = True

    def _define_frequency(self):
        """`_freq` (entity, phenotype, f): P(phenotype | entity) for every association that records
        one. A view, evaluated per query over only the entities that query touches: nothing is
        computed at startup.

        f is `has_quotient` (OMIM's "9 of 12 patients") when present, else the midpoint of the HPO
        frequency category (Orphanet), floored at MIN_FREQUENCY. An entity with the same phenotype
        from several sources takes the highest. A KG whose edges lack the frequency columns gets an
        empty view, so the tie-break falls back to the default frequency everywhere."""
        cols = {r[0] for r in self.con.execute("DESCRIBE src.edges").fetchall()}
        if not {"has_quotient", "frequency_qualifier", "category", "predicate"} <= cols:
            self.con.execute(
                "CREATE VIEW _freq AS SELECT NULL::VARCHAR AS entity, NULL::VARCHAR AS phenotype, NULL::DOUBLE AS f WHERE false"
            )
            return
        cases = " ".join(f"WHEN '{k}' THEN {v}" for k, v in FREQUENCY_CATEGORY_MIDPOINTS.items())
        negated = "AND NOT coalesce(try_cast(negated AS BOOLEAN), false)" if "negated" in cols else ""
        self.con.execute(f"""
            CREATE VIEW _freq AS
            SELECT entity, phenotype, greatest({MIN_FREQUENCY}, max(f)) AS f
            FROM (SELECT subject AS entity, object AS phenotype,
                         coalesce(try_cast(has_quotient AS DOUBLE), CASE frequency_qualifier {cases} END) AS f
                  FROM src.edges
                  WHERE category IN ('biolink:GeneToPhenotypicFeatureAssociation',
                                     'biolink:DiseaseToPhenotypicFeatureAssociation')
                    AND predicate = 'biolink:has_phenotype' {negated})
            WHERE f IS NOT NULL
            GROUP BY entity, phenotype""")

    def frequencies_batch(self, entity_ids) -> dict:
        """{(entity, phenotype) -> recorded frequency} for many entities in one query. Pairs with no
        recorded frequency are absent (the caller decides what a missing frequency means)."""
        ids = _dedupe(e for e in entity_ids if e)
        if not ids:
            return {}
        rows = self._read(
            f"SELECT entity, phenotype, f FROM _freq WHERE entity IN (SELECT unnest([{_quote_list(ids)}]::VARCHAR[]))"
        ).fetchall()
        return {(e, p): f for e, p, f in rows}

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

    def _all_pairs_detail(self, subjects, objects, ic_view="_ic") -> dict:
        """For every (subject term × object term): jaccard, resnik, phenodigm, and the MICA
        (max-IC shared ancestor). One DuckDB query. Pairs with no shared ancestor are omitted.

        `ic_view` is the IC to score with (see `ic_view()`). A shared ancestor with no row in it
        (possible with annotation IC, which has no rows for terms no annotation reaches) still
        counts toward Jaccard, with IC 0."""
        subj_q, obj_q = _quote_list(subjects), _quote_list(objects)
        rows = self._read(f"""
            WITH s_terms(t) AS (SELECT unnest([{subj_q}]::VARCHAR[])),
                 o_terms(t) AS (SELECT unnest([{obj_q}]::VARCHAR[])),
                 allterms AS (SELECT t FROM s_terms UNION SELECT t FROM o_terms),
                 qanc AS (SELECT DISTINCT s AS t, o AS a FROM _clo WHERE s IN (SELECT t FROM allterms)),
                 sizes AS (SELECT t, count(*) AS sz FROM qanc GROUP BY t),
                 -- one row per shared ancestor of each (s, o) pair, carrying its IC
                 common AS (
                   SELECT s.t AS s, o.t AS o, sa.a AS a, coalesce(icv.ic, 0.0) AS ic
                   FROM s_terms s JOIN o_terms o ON true
                   JOIN qanc sa ON sa.t = s.t
                   JOIN qanc oa ON oa.t = o.t AND oa.a = sa.a
                   LEFT JOIN {ic_view} icv ON icv.term = sa.a
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
        self,
        subjects,
        objects,
        metric="ancestor_information_content",
        direction="bidirectional",
        information_content=ONTOLOGY_IC,
        corpus_prefix=None,
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
        ic_view = self.ic_view(information_content, corpus_prefix)
        subj, obj = _dedupe(subjects), _dedupe(objects)
        pairs = self._all_pairs_detail(subj, obj, ic_view)
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

    def _termset_search(
        self,
        query_terms,
        metric,
        entity_filter,
        limit,
        direction="bidirectional",
        ic_view="_ic",
        tie_break=NO_TIE_BREAK,
        default_frequency=DEFAULT_FREQUENCY,
    ):
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
        tie_break = str(tie_break or NO_TIE_BREAK).lower()
        if tie_break not in (NO_TIE_BREAK, FREQUENCY_TIE_BREAK):
            raise ValueError(f"unknown tie_break {tie_break!r}")
        Q = _quote_list(set(query_terms))
        score_expr = spec.sql_rank
        lim = "" if limit is None else f"LIMIT {int(limit)}"
        if tie_break == FREQUENCY_TIE_BREAK:
            # For each query term, the frequency of the entity annotation that best matches it (the
            # most frequent one among equally good matches), summed in log space: the entity whose
            # matched phenotypes are most typical of it ranks first among equal scores.
            dflt = max(MIN_FREQUENCY, min(1.0, float(default_frequency)))
            tie_ctes = f""",
             qbest AS (SELECT e, q, max(score) AS best FROM ranked GROUP BY e, q),
             qfreq AS (SELECT r.e, r.q, max(coalesce(fq.f, {dflt})) AS f
                       FROM ranked r JOIN qbest b ON b.e = r.e AND b.q = r.q AND r.score = b.best
                       LEFT JOIN _freq fq ON fq.entity = r.e AND fq.phenotype = r.p
                       GROUP BY r.e, r.q),
             tie AS (SELECT e, sum(ln(f)) AS tb FROM qfreq GROUP BY e)"""
            tie_join = "LEFT JOIN tie ON tie.e = coalesce(d1.e, d2.e)"
            order = f"round(score, {_TIE_DECIMALS}) DESC, coalesce(tie.tb, -1e308) DESC, entity"
        else:
            tie_ctes, tie_join, order = "", "", "score DESC, entity"
        sql = f"""
        WITH qterms(q) AS (SELECT unnest([{Q}]::VARCHAR[])),
             q_anc AS (SELECT qt.q AS q, c.o AS a, coalesce(ic.ic, 0.0) AS ic
                       FROM qterms qt JOIN _clo c ON c.s = qt.q LEFT JOIN {ic_view} ic ON ic.term = c.o),
             qsize AS (SELECT q, count(*) AS sz FROM q_anc GROUP BY q),
             nq AS (SELECT count(*) AS n FROM qterms),
             -- DISTINCT: an entity may be annotated to the same phenotype via multiple association
             -- rows (different evidence/sources). Without dedup, p_anc repeats that phenotype's
             -- ancestors, inflating the count(*) intersection below past the union size -> a zero or
             -- negative jaccard denominator (inf score; sqrt-of-negative for phenodigm). psize already
             -- uses count(DISTINCT), so the two must agree.
             ent_ph AS (SELECT DISTINCT entity AS e, phenotype AS p FROM _assoc {entity_filter}),
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
                      GROUP BY bm.e){tie_ctes}
        SELECT coalesce(d1.e, d2.e) AS entity, {score_combiner} AS score
        FROM dir1 d1 FULL OUTER JOIN dir2 d2 ON d1.e = d2.e {tie_join}
        ORDER BY {order} {lim}
        """
        return self._read(sql).fetchall()

    def full_search(
        self,
        query_terms,
        *,
        limit=10,
        metric="ancestor_information_content",
        prefix=None,
        direction="bidirectional",
        information_content=ONTOLOGY_IC,
        tie_break=NO_TIE_BREAK,
        default_frequency=DEFAULT_FREQUENCY,
    ):
        """Score every entity (optionally restricted to CURIE `prefix`) by the termset
        best-match-average — one DuckDB query. Matches semsimian's Full mode; more accurate than
        Hybrid (no Jaccard prefilter dropping true-top entities)."""
        ic_view = self.ic_view(information_content, prefix)
        ef = f"WHERE split_part(entity, ':', 1) = {_quote_list([prefix])}" if prefix else ""
        return self._termset_search(
            query_terms, metric, ef, limit, direction, ic_view, tie_break=tie_break, default_frequency=default_frequency
        )

    def hybrid_search(
        self,
        query_terms,
        *,
        limit=10,
        metric="ancestor_information_content",
        prefix=None,
        direction="bidirectional",
        information_content=ONTOLOGY_IC,
        tie_break=NO_TIE_BREAK,
        default_frequency=DEFAULT_FREQUENCY,
    ):
        """Hybrid search — semsimian's production mode: cheap Jaccard prefilter then termset rerank,
        as one query over the candidate set. (The Jaccard prefilter is direction-agnostic; the
        rerank honors `direction`.)"""
        ic_view = self.ic_view(information_content, prefix)  # validate before the prefilter runs
        flat = self._flat(query_terms, prefix)
        if not flat:
            return []
        scores = sorted({j for _, j in flat}, reverse=True)
        k = max(math.ceil((limit / 1000.0) * len(scores)), limit)
        cutoff = scores[k] if k < len(scores) else scores[-1]
        candidates = [e for e, j in flat if j >= cutoff]
        ef = f"WHERE entity IN (SELECT unnest([{_quote_list(candidates)}]::VARCHAR[]))"
        return self._termset_search(
            query_terms, metric, ef, limit, direction, ic_view, tie_break=tie_break, default_frequency=default_frequency
        )

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

    def search(
        self,
        query_terms,
        *,
        limit=10,
        metric="ancestor_information_content",
        prefix=None,
        direction="bidirectional",
        mode="hybrid",
        information_content=ONTOLOGY_IC,
        tie_break=NO_TIE_BREAK,
        default_frequency=DEFAULT_FREQUENCY,
    ):
        """All-DuckDB search: rank entities (Hybrid by default; Full when `mode="full"`), then enrich
        the whole page with full termset detail in a constant number of queries — independent of
        `limit`, no per-result round-trips. Returns [(entity_id, score, comparison)] where
        `comparison` matches `termset_pairwise_similarity`'s shape (the entity's phenotypes are the
        subjects, the query terms the objects — so `comparison["average_score"]` equals `score`).
        Labels and entity hydration are added by the caller (also batched). `information_content`
        is "ontology" or "annotation"; annotation IC uses the corpus of `prefix` entities."""
        spec = _METRICS.get(metric.lower())
        if spec is None:
            raise ValueError(f"unknown metric {metric!r}")
        ic_view = self.ic_view(information_content, prefix)
        ranker = self.full_search if mode == "full" else self.hybrid_search
        ranked = ranker(
            query_terms,
            limit=limit,
            metric=metric,
            prefix=prefix,
            direction=direction,
            information_content=information_content,
            tie_break=tie_break,
            default_frequency=default_frequency,
        )
        if not ranked:
            return []
        entity_ids = [e for e, _ in ranked]
        pheno_by_entity = self.entity_phenotypes_batch(entity_ids)
        obj = _dedupe(query_terms)
        # every phenotype across the page, scored against the query once (single DuckDB query); each
        # entity then reuses the relevant slice of this `pairs` map when shaped below.
        all_phenos = _dedupe(p for e in entity_ids for p in pheno_by_entity.get(e, []))
        pairs = self._all_pairs_detail(all_phenos, obj, ic_view)
        freq = self.frequencies_batch(entity_ids)
        out = []
        for entity_id, score in ranked:
            subj = _dedupe(pheno_by_entity.get(entity_id, []))
            comparison = self._shape_comparison(subj, obj, pairs, spec.detail_key, metric, direction)
            # the recorded frequency of the entity's phenotype in each match (subjects are the
            # entity's phenotypes; for object matches it's the matched target), when there is one
            for source, bm in comparison["subject_best_matches"].items():
                bm["frequency"] = freq.get((entity_id, source))
            for bm in comparison["object_best_matches"].values():
                bm["frequency"] = freq.get((entity_id, bm["match_target"]))
            out.append((entity_id, score, comparison))
        return out
