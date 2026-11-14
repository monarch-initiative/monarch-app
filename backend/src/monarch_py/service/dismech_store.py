"""Experimental: dismech integrations served from a prebuilt dismech.duckdb.

The file (built by scripts/dismech_db.py from one pinned dismech release) holds dismech's
content in the ``core`` schema and the KG slices it is joined to in ``app``. It is attached
READ_ONLY, so a worker starts in milliseconds and many workers share one file through the OS
page cache. dismech stays out of the KG.
"""

from collections import defaultdict
from pathlib import Path

import duckdb

from monarch_py.service.phenotype_profile import frequency_score, rank_key

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

_KG_DISEASES = f"""
SELECT subject AS disease_id, any_value(subject_label) AS label, {_NEGATED}, {_OBSERVATIONS}
FROM dm.app.kg_phenotype_disease
WHERE object_key = {_ID_KEY} AND object = $id
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

# dismech records of a phenotype or any of its subclasses, across diseases
_PHENOTYPE_RECORDS = f"""
WITH sub AS (
  SELECT hpo_id FROM dm.app.hp_closure WHERE ancestor_key = {_ID_KEY} AND ancestor_id = $id
)
SELECT CASE WHEN hpo_id = $id THEN 'exact' ELSE 'more_specific' END AS match, {_RECORD}
FROM dm.core.phenotype WHERE hpo_id IN (SELECT hpo_id FROM sub) AND mondo_id IS NOT NULL
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
        """diseases with a phenotype, collapsed across KG sources, with dismech corroboration.

        dismech records of the phenotype or a subclass of it corroborate the disease's row; records
        for a disease without a KG row for this phenotype come back as dismech_only rows.
        """
        params = {"id": phenotype_id}
        rows = self._rows(_KG_DISEASES, params)
        for row in rows:
            _init_row(row)
        by_disease = {r["disease_id"]: r for r in rows if not r["negated"]}
        unmatched = []
        for m in self._rows(_PHENOTYPE_RECORDS, params):
            target = by_disease.get(m["mondo_id"])
            if target is not None:
                target["dismech"].append(m)
            else:
                unmatched.append({**m, "match": "dismech_only", "specific_match": m["match"]})
        labels = self._disease_labels({m["mondo_id"] for m in unmatched})
        rows += _dismech_only_rows(
            unmatched,
            key="mondo_id",
            row=lambda r: {"disease_id": r["mondo_id"], "label": labels.get(r["mondo_id"]) or r["disorder"]},
        )
        return {"id": phenotype_id, "release": self.release, **self._finish(rows, **page)}

    def _finish(self, rows, corroborated_only=False, dismech_only=False, limit=None, offset=0):
        """rank, filter, then page; counts describe every row, before filtering"""
        for row in rows:
            row["frequency_score"] = frequency_score(row)
        rows.sort(key=rank_key)
        counts = {
            "kg_total": sum(1 for r in rows if not r["dismech_only"]),
            "dismech_corroborated": sum(1 for r in rows if r["dismech"] and not r["dismech_only"]),
            "dismech_unmatched": sum(1 for r in rows if r["dismech_only"]),
        }
        rows = [r for r in rows if (dismech_only or not r["dismech_only"]) and (not corroborated_only or r["dismech"])]
        page = rows[offset : offset + limit if limit else None]
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

    # treatments

    def treatments(self, node_id: str) -> dict:
        """dismech treatments for a disease (MONDO), or the diseases a drug (CHEBI/NCIT) treats"""
        if node_id.startswith("MONDO:"):
            rows = self._rows(
                f"SELECT {_TREATMENT_COLUMNS} FROM dm.core.treatment "
                f"WHERE {_ID_KEY.replace('$id', 'mondo_id')} = {_ID_KEY} AND mondo_id = $id ORDER BY name",
                {"id": node_id},
            )
        else:
            rows = self._rows(
                f"SELECT {_TREATMENT_COLUMNS} FROM dm.core.treatment "
                "WHERE list_contains(list_transform(agents, a -> a.id), $id) ORDER BY disorder, name",
                {"id": node_id},
            )
        known = self.kg_nodes(
            {a["id"] for r in rows for a in r["agents"]} | {r["mondo_id"] for r in rows if r["mondo_id"]}
        )
        for r in rows:
            for a in r["agents"]:
                a["in_kg"] = a["id"] in known
                a["label"] = a["label"] or (known.get(a["id"]) or {}).get("name")
        targets = {m["node_id"] for r in rows for m in r["target_mechanisms"] if m["resolved"]}
        return {
            "id": node_id,
            "release": self.release,
            "rows": rows,
            "mechanism_nodes": self.nodes(targets),
        }

    # mechanisms by ontology term

    def mechanisms(self, term_id: str) -> dict:
        """dismech mechanism nodes annotated with a GO/CL/UBERON/CHEBI/HGNC term, and the phenotypes
        each one leads to"""
        rows = self._rows(
            "SELECT mondo_id, disorder, disorder_file, node_id, node_name, list(DISTINCT slot) AS slots, "
            "any_value(modifier) AS modifier FROM dm.core.descriptor WHERE term_id = $id "
            "GROUP BY ALL ORDER BY disorder, node_name",
            {"id": term_id},
        )
        node_ids = sorted({r["node_id"] for r in rows})
        leads_to = defaultdict(list)
        if node_ids:
            for p in self._rows(
                "SELECT node_id, hpo_id, hpo_label, diagnostic FROM dm.core.phenotype_mechanism "
                "WHERE node_id IN (SELECT unnest($ids)) ORDER BY diagnostic DESC, hpo_label",
                {"ids": node_ids},
            ):
                leads_to[p.pop("node_id")].append(p)
        for r in rows:
            r["leads_to"] = leads_to.get(r["node_id"], [])
        return {
            "id": term_id,
            "release": self.release,
            "label": (self.kg_nodes({term_id}).get(term_id) or {}).get("name"),
            "rows": rows,
            "mechanism_nodes": self.nodes(set(node_ids)),
        }

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


def _json(value):
    import json

    return json.loads(value) if isinstance(value, str) else value


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
