"""Experimental: dismech integrations served from a prebuilt dismech.duckdb.

The file (built by scripts/dismech_db.py from one pinned dismech release) holds dismech's
content in the ``core`` schema and the KG slices it is joined to in ``app``. It is attached
READ_ONLY, so a worker starts in milliseconds and many workers share one file through the OS
page cache. dismech stays out of the KG.
"""

import re
from collections import defaultdict
from pathlib import Path

import duckdb

from monarch_py.service.phenotype_profile import FREQUENCY_BAND_FLOOR, frequency_score, rank_key

# numeric local id, matching the sort key the build uses
_ID_KEY = "try_cast(split_part($id, ':', 2) AS BIGINT)"

_OBSERVATIONS = """
  list({
    'source': primary_knowledge_source, 'record': original_subject,
    'frequency': frequency_qualifier, 'frequency_label': frequency_qualifier_label,
    'percentage': try_cast(has_percentage AS DOUBLE),
    'count': try_cast(has_count AS INTEGER), 'total': try_cast(has_total AS INTEGER),
    'onset': onset_qualifier_label, 'sex': sex_qualifier_label,
    'publications': publications, 'evidence': has_evidence
  } ORDER BY primary_knowledge_source) AS observations
"""

_NEGATED = "coalesce(lower(cast(negated AS VARCHAR)) = 'true', false) AS negated"

# dismech phenotype record fields carried on a row
_RECORD = (
    "hpo_id, hpo_label, phenotype_name, mondo_id, disorder, disorder_file, diagnostic, frequency_hp, "
    "frequency_text, evidence, nearest_mechanisms, phenotype_node_id, upstream_edges"
)

_KG_PHENOTYPES = f"""
SELECT object AS hpo_id, any_value(object_label) AS label, {_NEGATED}, {_OBSERVATIONS}
FROM dm.app.kg_disease_phenotype
WHERE subject_key = {_ID_KEY} AND subject = $id
GROUP BY object, negated
"""

# a phenotype page's KG edges: those to the term or anything under it in the KG's closure
# (subclasses, and for an anatomy or process term, the phenotypes affecting it), as the stock
# association table counts them
_UNDER_TERM = (
    "SEMI JOIN dm.app.hp_closure c ON c.hpo_id = p.object "
    f"AND c.ancestor_key IS NOT DISTINCT FROM {_ID_KEY} AND c.ancestor_id = $id"
)

# one observation's frequency estimate, as phenotype_profile.frequency_score reads it
_OBSERVATION_SCORE = f"""CASE
  WHEN k IS NOT NULL AND n > 0 THEN greatest(0, (k / n + 3.8416 / (2 * n)
    - 1.96 * sqrt((k / n * (1 - k / n) + 3.8416 / (4 * n)) / n)) / (1 + 3.8416 / n))
  WHEN pct IS NOT NULL THEN pct / 100
  ELSE CASE band {" ".join(f"WHEN '{k}' THEN {v}" for k, v in FREQUENCY_BAND_FLOOR.items())} END
END"""

# a high-level term reaches every disease, so a phenotype page ranks on one summary row per
# (disease, negated) and only loads the observations of the page it shows
_KG_DISEASE_SUMMARY = f"""
WITH e AS (
  SELECT subject, subject_label, object_label, {_NEGATED}, primary_knowledge_source AS source,
    try_cast(has_count AS DOUBLE) AS k, try_cast(has_total AS DOUBLE) AS n,
    try_cast(has_percentage AS DOUBLE) AS pct, frequency_qualifier AS band
  FROM dm.app.kg_phenotype_disease p {_UNDER_TERM}
)
SELECT subject AS disease_id, any_value(subject_label) AS label, negated,
  coalesce(list(DISTINCT source ORDER BY source) FILTER (WHERE source IS NOT NULL), []) AS sources,
  avg({_OBSERVATION_SCORE}) AS kg_score, {{terms}} AS terms
FROM e GROUP BY subject, negated
"""

_KG_DISEASE_OBSERVATIONS = f"""
SELECT subject AS disease_id, {_NEGATED},
  list({{
    'source': primary_knowledge_source, 'record': original_subject,
    'phenotype': object, 'phenotype_label': object_label,
    'frequency': frequency_qualifier, 'frequency_label': frequency_qualifier_label,
    'percentage': try_cast(has_percentage AS DOUBLE),
    'count': try_cast(has_count AS INTEGER), 'total': try_cast(has_total AS INTEGER)
  }} ORDER BY primary_knowledge_source, object) AS observations
FROM dm.app.kg_phenotype_disease p {_UNDER_TERM}
WHERE subject IN (SELECT unnest($diseases))
GROUP BY subject, negated
"""

# dismech records for a disease, with every KG phenotype they corroborate: the same HP term,
# or a KG term the dismech term is a subclass of
_DISEASE_MATCHES = f"""
WITH dm AS (
  SELECT * FROM dm.core.phenotype
  WHERE {_ID_KEY.replace("$id", "mondo_id")} = {_ID_KEY} AND mondo_id = $id AND hpo_id LIKE 'HP:%'
)
SELECT c.ancestor_id AS kg_hpo_id,
  CASE WHEN dm.hpo_id = c.ancestor_id THEN 'exact' ELSE 'more_specific' END AS match,
  {", ".join("dm." + c.strip() for c in _RECORD.split(","))}
FROM dm JOIN dm.app.hp_closure c ON c.hpo_id = dm.hpo_id
WHERE c.ancestor_id IN (SELECT unnest($kg_hpo))
"""

# dismech records of a phenotype or anything under it, across diseases
_UNDER_TERM_RECORDS = f"""
FROM dm.core.phenotype WHERE mondo_id IS NOT NULL AND hpo_id IN (
  SELECT hpo_id FROM dm.app.hp_closure
  WHERE ancestor_key IS NOT DISTINCT FROM {_ID_KEY} AND ancestor_id = $id
)"""

_PHENOTYPE_RECORD_SUMMARY = f"""
SELECT mondo_id, any_value(disorder) AS disorder, bool_or(diagnostic) AS diagnostic,
  avg(CASE frequency_hp {" ".join(f"WHEN '{k}' THEN {v}" for k, v in FREQUENCY_BAND_FLOOR.items())} END) AS score,
  {{terms}} AS terms
{_UNDER_TERM_RECORDS}
GROUP BY mondo_id
"""

_PHENOTYPE_RECORDS = f"""
SELECT CASE WHEN hpo_id = $id THEN 'exact' ELSE 'more_specific' END AS match, {_RECORD}
{_UNDER_TERM_RECORDS} AND mondo_id IN (SELECT unnest($diseases))
"""

_TREATMENT_COLUMNS = (
    "mondo_id, disorder, disorder_file, treatment_node_id, name, description, modality, action_category, "
    "treatment_term_id, treatment_term_label, agents, target_mechanisms, target_phenotypes, evidence"
)


class DismechStore:
    def __init__(self, con: duckdb.DuckDBPyConnection):
        self.con = con
        self.release = con.execute("SELECT release FROM dm.core.release").fetchone()[0]

    @classmethod
    def open(cls, path: str, memory_limit="1GB", threads=2):
        if not Path(path).exists():
            raise FileNotFoundError(path)
        con = duckdb.connect()
        con.execute(f"SET memory_limit = '{memory_limit.replace(chr(39), '')}'")
        con.execute(f"SET threads = {int(threads)}")
        con.execute(f"ATTACH '{str(path).replace(chr(39), chr(39) * 2)}' AS dm (READ_ONLY)")
        return cls(con)

    def _rows(self, sql, params):
        cur = self.con.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    # phenotype profiles

    def phenotype_profile(self, disease_id: str, **page) -> dict:
        """a disease's phenotypes, collapsed across KG sources, with dismech corroboration"""
        params = {"id": disease_id}
        rows = self._rows(_KG_PHENOTYPES, params)
        for row in rows:
            _init_row(row)
        by_hpo = {r["hpo_id"]: r for r in rows if not r["negated"]}
        matched = set()
        for m in self._rows(_DISEASE_MATCHES, {**params, "kg_hpo": sorted(by_hpo)}):
            by_hpo[m.pop("kg_hpo_id")]["dismech"].append(m)
            matched.add(m["phenotype_node_id"])
        records = self._rows(
            f"SELECT 'dismech_only' AS match, {_RECORD} FROM dm.core.phenotype "
            f"WHERE {_ID_KEY.replace('$id', 'mondo_id')} = {_ID_KEY} AND mondo_id = $id AND hpo_id LIKE 'HP:%'",
            params,
        )
        rows += _dismech_only_rows(
            (r for r in records if r["phenotype_node_id"] not in matched),
            key="hpo_id",
            row=lambda r: {"hpo_id": r["hpo_id"], "label": r["hpo_label"]},
        )
        return {"id": disease_id, "release": self.release, **self._finish(rows, **page)}

    def phenotype_diseases(self, phenotype_id: str, **page) -> dict:
        """diseases with a phenotype or anything under it, collapsed across KG sources, with
        dismech corroboration.

        dismech records under the term corroborate the disease's row; records for a disease
        without a KG row come back as dismech_only rows. rows are ranked on summaries, and only
        the page shown gets its observations and records.
        """
        params = {"id": phenotype_id}
        searching = bool(page.get("search"))
        records = {
            r["mondo_id"]: r
            for r in self._rows(
                _PHENOTYPE_RECORD_SUMMARY.format(
                    terms="string_agg(DISTINCT hpo_label || ' ' || phenotype_name, ' | ')" if searching else "NULL"
                ),
                params,
            )
        }
        rows, matched = [], set()
        kg = self._rows(
            _KG_DISEASE_SUMMARY.format(terms="string_agg(DISTINCT object_label, ' | ')" if searching else "NULL"),
            params,
        )
        for row in kg:
            record = None if row["negated"] else records.get(row["disease_id"])
            if record:
                matched.add(row["disease_id"])
            score = row.pop("kg_score")
            # the record summary stands in for the records until the row is on the page
            terms = [row.pop("terms"), record and record["terms"]]
            rows.append({**row, "dismech": [record] if record else [], "dismech_only": False, "_terms": terms})
            rows[-1]["frequency_score"] = score if score is not None else record and record["score"]
        unmatched = [r for id, r in records.items() if id not in matched]
        labels = self._disease_labels({r["mondo_id"] for r in unmatched})
        for r in unmatched:
            rows.append(
                {
                    "disease_id": r["mondo_id"],
                    "label": labels.get(r["mondo_id"]) or r["disorder"],
                    "negated": False,
                    "sources": [],
                    "dismech": [r],
                    "dismech_only": True,
                    "frequency_score": r["score"],
                    "_terms": [r["terms"]],
                }
            )

        def hydrate(page):
            ids = sorted({r["disease_id"] for r in page})
            observations = {
                (o["disease_id"], o["negated"]): o["observations"]
                for o in self._rows(_KG_DISEASE_OBSERVATIONS, {**params, "diseases": ids})
            }
            full = defaultdict(list)
            for m in self._rows(_PHENOTYPE_RECORDS, {**params, "diseases": ids}):
                full[m["mondo_id"]].append(m)
            for row in page:
                row["observations"] = observations.get((row["disease_id"], row["negated"]), [])
                if row["dismech_only"]:
                    row["dismech"] = [
                        {**m, "match": "dismech_only", "specific_match": m["match"]} for m in full[row["disease_id"]]
                    ]
                elif row["dismech"]:
                    row["dismech"] = full[row["disease_id"]]

        return {"id": phenotype_id, "release": self.release, **self._finish(rows, hydrate=hydrate, **page)}

    def _finish(
        self, rows, corroborated_only=False, dismech_only=False, search=None, limit=None, offset=0, hydrate=None
    ):
        """rank, filter, then page; counts describe every row, before filtering. `hydrate` fills
        in the page's rows when they were ranked on summaries."""
        for row in rows:
            if "frequency_score" not in row:
                row["frequency_score"] = frequency_score(row)
        rows.sort(key=rank_key)
        counts = {
            "kg_total": sum(1 for r in rows if not r["dismech_only"]),
            "dismech_corroborated": sum(1 for r in rows if r["dismech"] and not r["dismech_only"]),
            "dismech_unmatched": sum(1 for r in rows if r["dismech_only"]),
        }
        rows = [
            r
            for r in rows
            if (dismech_only or not r["dismech_only"])
            and (not corroborated_only or r["dismech"])
            and _matches(r, search)
        ]
        for r in rows:
            r.pop("_terms", None)
        page = rows[offset : offset + limit if limit else None]
        if hydrate:
            hydrate(page)
        return {
            "total": len(rows),
            "rows": page,
            "dismech_available": True,
            **counts,
            "mechanism_nodes": self.nodes(
                {m["phenotype_node_id"] for r in page for m in r["dismech"]}
                | {
                    x
                    for r in page
                    for m in r["dismech"]
                    for e in m["upstream_edges"]
                    for x in (e["source"], e["target"])
                }
            ),
        }

    def _disease_labels(self, ids):
        if not ids:
            return {}
        rows = self._rows(
            "SELECT DISTINCT subject AS id, subject_label AS label FROM dm.app.kg_disease_phenotype "
            "WHERE subject IN (SELECT unnest($ids))",
            {"ids": sorted(ids)},
        )
        return {r["id"]: r["label"] for r in rows}

    def nodes(self, ids) -> dict:
        """hover details for dismech mechanism / phenotype nodes, by node id"""
        if not ids:
            return {}
        rows = self._rows(
            "SELECT node_id, kind, name, term_id, description, biological_scale, frequency, descriptors, "
            "evidence FROM dm.core.node WHERE node_id IN (SELECT unnest($ids))",
            {"ids": sorted(ids)},
        )
        return {r.pop("node_id"): r for r in rows}

    # gene <-> disease

    def gene_disease_profile(
        self, node_id: str, kind: str, corroborated_only=False, dismech_only=False, search=None, limit=None, offset=0
    ) -> dict:
        """a gene's diseases (HGNC) or a disease's genes (MONDO) in one KG association category
        (causal / correlated), collapsed across sources, with dismech's genetics records for the pair
        and the gene's mechanisms in that disease.

        A dismech record corroborates the KG row for the same pair in either category; it becomes a
        dismech_only row only when the KG has the pair in neither, in the category dismech gives it.
        """
        by_gene = node_id.startswith("HGNC:")
        table, key, other = (
            ("kg_gene_disease", "subject", "object") if by_gene else ("kg_disease_gene", "object", "subject")
        )
        id_col = "disease_id" if by_gene else "gene_id"
        kg = self._rows(
            f"SELECT category, {other} AS other_id, any_value({other}_label) AS label, list({{"
            "'source': primary_knowledge_source, 'predicate': predicate, 'record': original_subject, "
            "'publications': publications, 'evidence': has_evidence} ORDER BY primary_knowledge_source) AS observations "
            f"FROM dm.app.{table} WHERE {key}_key = {_ID_KEY} AND {key} = $id GROUP BY category, {other}",
            {"id": node_id},
        )
        category = {
            "causal": "biolink:CausalGeneToDiseaseAssociation",
            "correlated": "biolink:CorrelatedGeneToDiseaseAssociation",
        }[kind]
        in_kg = {r["other_id"] for r in kg}
        rows = []
        for r in kg:
            if r["category"] == category:
                rows.append({id_col: r["other_id"], "label": r["label"], "observations": r["observations"]})
        for row in rows:
            row["dismech"] = []
            row["dismech_only"] = False
            row["sources"] = sorted({o["source"] for o in row["observations"] if o["source"]})
        records = self._rows(
            "SELECT gene_id, symbol, mondo_id, disorder, disorder_file, relationship_type, association, kind, "
            "variant_origin, validity, notes, evidence FROM dm.core.gene "
            f"WHERE {'gene_id' if by_gene else 'mondo_id'} = $id",
            {"id": node_id},
        )
        here = {row[id_col]: row for row in rows}
        unmatched = []
        for rec in records:
            other_id = rec["mondo_id"] if by_gene else rec["gene_id"]
            if other_id in here:
                here[other_id]["dismech"].append(rec)
            elif other_id not in in_kg and rec["kind"] == kind:
                unmatched.append(rec)
        labels = self.kg_nodes({(r["mondo_id"] if by_gene else r["gene_id"]) for r in unmatched})
        rows += _dismech_only_rows(
            unmatched,
            key="mondo_id" if by_gene else "gene_id",
            row=lambda r: {
                id_col: r["mondo_id"] if by_gene else r["gene_id"],
                "label": (labels.get(r["mondo_id"] if by_gene else r["gene_id"]) or {}).get("name")
                or (r["disorder"] if by_gene else r["symbol"]),
            },
        )
        rows.sort(key=lambda r: (r["dismech_only"], -len(r["sources"]), not r["dismech"], (r["label"] or "").lower()))
        counts = {
            "kg_total": sum(1 for r in rows if not r["dismech_only"]),
            "dismech_corroborated": sum(1 for r in rows if r["dismech"] and not r["dismech_only"]),
            "dismech_unmatched": sum(1 for r in rows if r["dismech_only"]),
        }
        rows = [
            r
            for r in rows
            if (dismech_only or not r["dismech_only"])
            and (not corroborated_only or r["dismech"])
            and _matches(r, search)
        ]
        page = rows[offset : offset + limit if limit else None]
        records = [m for r in page for m in r["dismech"]]
        self._gene_mechanisms(records)
        node_ids = {m["node_id"] for rec in records for m in rec["mechanisms"]} | {
            x for rec in records for e in rec["edges"] for x in (e["source"], e["target"])
        }
        return {
            "id": node_id,
            "release": self.release,
            "kind": kind,
            "total": len(rows),
            "rows": page,
            "dismech_available": True,
            **counts,
            "mechanism_nodes": self.nodes(node_ids),
        }

    def _gene_mechanisms(self, records):
        """add each genetics record's mechanisms (nodes annotated with its gene in its disorder), the
        phenotypes downstream of them, and the edges leading there"""
        if not records:
            return
        found = defaultdict(list)
        for m in self._rows(
            "SELECT term_id, disorder_file, node_id, node_name, list(DISTINCT slot ORDER BY slot) AS slots "
            "FROM dm.core.descriptor WHERE term_id IN (SELECT unnest($genes)) "
            "AND disorder_file IN (SELECT unnest($files)) GROUP BY ALL ORDER BY node_name",
            {"genes": sorted({r["gene_id"] for r in records}), "files": sorted({r["disorder_file"] for r in records})},
        ):
            found[(m["term_id"], m["disorder_file"])].append(
                {"node_id": m["node_id"], "name": m["node_name"], "slots": m["slots"]}
            )
        for rec in records:
            rec["mechanisms"] = found.get((rec["gene_id"], rec["disorder_file"]), [])
        self._downstream(records)

    # treatments

    def treatments(self, node_id: str, name: str | None = None) -> dict:
        """dismech treatments for a disease (MONDO), or the diseases a drug treats, each with the
        phenotypes downstream of its target mechanisms and the edges leading there.

        A drug matches a treatment by agent id, or, given its name, by that name as a whole word in
        the treatment's name or an agent's label: dismech often names a drug without an agent term.
        """
        if node_id.startswith("MONDO:"):
            rows = self._rows(
                f"SELECT {_TREATMENT_COLUMNS} FROM dm.core.treatment "
                f"WHERE {_ID_KEY.replace('$id', 'mondo_id')} = {_ID_KEY} AND mondo_id = $id ORDER BY name",
                {"id": node_id},
            )
        else:
            rows = self._rows(
                f"SELECT {_TREATMENT_COLUMNS} FROM dm.core.treatment "
                "WHERE list_contains(list_transform(agents, a -> a.id), $id) OR ($word IS NOT NULL AND ("
                "  regexp_matches(lower(name), $word)"
                "  OR len(list_filter(agents, a -> regexp_matches(lower(coalesce(a.label, '')), $word))) > 0"
                ")) ORDER BY disorder, name",
                {"id": node_id, "word": rf"\b{re.escape(name.lower())}\b" if name and len(name) > 2 else None},
            )
        known = self.kg_nodes(
            {a["id"] for r in rows for a in r["agents"]} | {r["mondo_id"] for r in rows if r["mondo_id"]}
        )
        for r in rows:
            for a in r["agents"]:
                a["in_kg"] = a["id"] in known
                a["label"] = a["label"] or (known.get(a["id"]) or {}).get("name")
        # the phenotypes downstream of each treatment's targets, for its mechanism graph
        for r in rows:
            r["mechanisms"] = [{"node_id": m["node_id"]} for m in r["target_mechanisms"] if m["resolved"]]
        self._downstream(rows)
        for r in rows:
            del r["mechanisms"]
        node_ids = {m["node_id"] for r in rows for m in r["target_mechanisms"] if m["resolved"]} | {
            x for r in rows for e in r["edges"] for x in (e["source"], e["target"])
        }
        return {
            "id": node_id,
            "release": self.release,
            "rows": rows,
            "mechanism_nodes": self.nodes(node_ids),
        }

    # diseases by mechanism term

    def term_diseases(self, term_id: str, limit: int | None = None, offset: int = 0) -> dict:
        """diseases whose dismech mechanisms are annotated with a GO/CL/UBERON term, one row per disease.

        Each row carries the matching mechanisms, the phenotypes downstream of them, and the causal
        edges from those mechanisms to those phenotypes, for one merged graph per disease.
        """
        mechanisms = self._rows(
            "SELECT mondo_id, disorder, disorder_file, node_id, node_name, list(DISTINCT slot ORDER BY slot) AS slots "
            "FROM dm.core.descriptor WHERE term_id = $id GROUP BY ALL ORDER BY node_name",
            {"id": term_id},
        )
        diseases = {}
        for m in mechanisms:
            row = diseases.setdefault(
                m["disorder_file"],
                {
                    "disease_id": m["mondo_id"],
                    "disorder": m["disorder"],
                    "disorder_file": m["disorder_file"],
                    "mechanisms": [],
                },
            )
            row["mechanisms"].append({"node_id": m["node_id"], "name": m["node_name"], "slots": m["slots"]})
        labels = self.kg_nodes({r["disease_id"] for r in diseases.values() if r["disease_id"]})
        for row in diseases.values():
            row["label"] = (labels.get(row["disease_id"]) or {}).get("name") or row["disorder"]
            row["slots"] = sorted({s for m in row["mechanisms"] for s in m["slots"]})
        rows = sorted(diseases.values(), key=lambda r: (-len(r["mechanisms"]), r["label"].lower()))
        page = rows[offset : offset + limit if limit else None]
        self._downstream(page)
        node_ids = {m["node_id"] for r in page for m in r["mechanisms"]} | {
            x for r in page for e in r["edges"] for x in (e["source"], e["target"])
        }
        return {
            "id": term_id,
            "release": self.release,
            "label": (self.kg_nodes({term_id}).get(term_id) or {}).get("name"),
            "total": len(rows),
            "rows": page,
            "mechanism_nodes": self.nodes(node_ids),
        }

    def _downstream(self, rows):
        """add each row's phenotypes downstream of its mechanisms, and the edges leading there"""
        ids = sorted({m["node_id"] for r in rows for m in r["mechanisms"]})
        reached = defaultdict(list)
        if ids:
            for p in self._rows(
                "SELECT DISTINCT pm.node_id, p.disorder_file, p.hpo_id, p.hpo_label, p.diagnostic, p.upstream_edges "
                "FROM dm.core.phenotype_mechanism pm "
                "JOIN dm.core.phenotype p ON p.phenotype_node_id = pm.phenotype_node_id "
                "WHERE pm.node_id IN (SELECT unnest($ids))",
                {"ids": ids},
            ):
                reached[p["disorder_file"]].append(p)
        for row in rows:
            start = {m["node_id"] for m in row["mechanisms"]}
            phenotypes, edges = {}, {}
            for p in reached.get(row["disorder_file"], []):
                if p["node_id"] not in start:
                    continue
                seen = phenotypes.setdefault(
                    p["hpo_id"], {"hpo_id": p["hpo_id"], "label": p["hpo_label"], "diagnostic": False}
                )
                seen["diagnostic"] = seen["diagnostic"] or p["diagnostic"]
                for e in p["upstream_edges"]:
                    edges[(e["source"], e["target"])] = e
            row["leads_to"] = sorted(
                phenotypes.values(), key=lambda p: (not p["diagnostic"], (p["label"] or "").lower())
            )
            row["edges"] = _reachable(edges.values(), start)

    def kg_nodes(self, ids) -> dict:
        if not ids:
            return {}
        rows = self._rows(
            "SELECT id, name, category FROM dm.app.kg_node WHERE id IN (SELECT unnest($ids))", {"ids": sorted(ids)}
        )
        return {r.pop("id"): r for r in rows}

    # pathographs

    def pathograph_graphs(self, node_id: str) -> list[tuple[str, str, str | None, dict]]:
        """(mondo id, name, dismech slug, graph) for a disease's pathograph, or every pathograph a gene
        appears in; the same shape the published per-disorder JSON files have"""
        if node_id.startswith("MONDO:"):
            mondo_ids = [node_id]
        else:
            mondo_ids = [
                r["mondo_id"]
                for r in self._rows("SELECT mondo_id FROM dm.core.pathograph_gene WHERE gene_id = $id", {"id": node_id})
            ]
        if not mondo_ids:
            return []
        disorders = self._rows(
            "SELECT mondo_id, file, name, slug FROM dm.core.pathograph_disorder "
            "WHERE mondo_id IN (SELECT unnest($ids)) ORDER BY mondo_id, file",
            {"ids": mondo_ids},
        )
        files = sorted({d["file"] for d in disorders})
        graphs = {f: {"nodes": [], "edges": []} for f in files}
        for n in self._rows(
            "SELECT file, id, node_type, color, is_orphan, description, meta FROM dm.core.pathograph_node "
            "WHERE file IN (SELECT unnest($files)) ORDER BY file, ord",
            {"files": files},
        ):
            graphs[n.pop("file")]["nodes"].append(n)
        for e in self._rows(
            "SELECT file, source, target, predicate, description FROM dm.core.pathograph_edge "
            "WHERE file IN (SELECT unnest($files)) ORDER BY file, ord",
            {"files": files},
        ):
            graphs[e.pop("file")]["edges"].append(e)
        for g in graphs.values():
            for n in g["nodes"]:
                n["meta"] = _json(n["meta"])
        return [(d["mondo_id"], d["name"] or d["mondo_id"], d["slug"], graphs[d["file"]]) for d in disorders]


def _reachable(edges, start):
    """the edges on paths leaving `start`: a phenotype's upstream subgraph also holds causes that
    have nothing to do with the term"""
    children = defaultdict(list)
    for e in edges:
        children[e["source"]].append(e)
    keep, todo, seen = [], list(start), set(start)
    while todo:
        for e in children.get(todo.pop(), []):
            keep.append(e)
            if e["target"] not in seen:
                seen.add(e["target"])
                todo.append(e["target"])
    return keep


def _json(value):
    import json

    return json.loads(value) if isinstance(value, str) else value


def _matches(row, search):
    """every word of a table search appears in the row's label or id, or in the terms behind
    it: a phenotype page's annotated subclasses, and dismech's phenotypes"""
    if not search:
        return True
    text = " ".join(
        filter(
            None,
            [
                row.get("label"),
                row.get("hpo_id"),
                row.get("disease_id"),
                row.get("gene_id"),
                *row.get("_terms", []),
                *(f"{m.get('hpo_label') or ''} {m.get('phenotype_name') or ''}" for m in row["dismech"]),
            ],
        )
    ).lower()
    return all(word in text for word in search.lower().split())


def _init_row(row):
    row["dismech"] = []
    row["dismech_only"] = False
    row["sources"] = sorted({o["source"] for o in row["observations"] if o["source"]})


def _dismech_only_rows(records, key, row):
    """dismech records that corroborate no KG row, grouped into one row per `key`"""
    grouped = {}
    for r in records:
        target = grouped.setdefault(
            r[key],
            {**row(r), "negated": False, "observations": [], "sources": [], "dismech": [], "dismech_only": True},
        )
        target["dismech"].append(r)
    return list(grouped.values())
