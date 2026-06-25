#!/usr/bin/env python3
"""Bake a slim, ducksim-ready DuckDB from monarch-kg.duckdb.

The api uses the duckdb file ONLY for ducksim similarity, which touches just:
  closure (rdfs:subClassOf rows), edges (Gene/Disease has_phenotype), nodes (id,name).
So we build a slim copy with exactly those, plus two precomputed tables the engine reads instead of
building at startup:
  ducksim_ic    (term -> IC)            -- removes the per-worker IC build
  ducksim_esize (entity -> |closure|)   -- removes the per-worker fan-out build (the memory spike)

Result: a much smaller artifact (lighter page-cache footprint, faster upload) and ~instant per-worker
startup. The SQL matches the engine's runtime build (service/ducksim.py). One-off for now; the same
logic should eventually move into the monarch-ingest build.

Usage:  python3 bake_ducksim.py IN.duckdb OUT.duckdb
"""
import sys

import duckdb

src, out = sys.argv[1], sys.argv[2]
P = "rdfs:subClassOf"
con = duckdb.connect(out)  # new, empty
con.execute(f"ATTACH '{src}' AS s (READ_ONLY)")

print("slim closure (subClassOf) ...", flush=True)
con.execute(f"""CREATE TABLE closure AS
    SELECT subject_id, predicate_id, object_id FROM s.closure WHERE predicate_id = '{P}'""")
print("slim edges (Gene/Disease has_phenotype) ...", flush=True)
con.execute("""CREATE TABLE edges AS
    SELECT subject, object, category, predicate, negated FROM s.edges
    WHERE category IN ('biolink:GeneToPhenotypicFeatureAssociation',
                       'biolink:DiseaseToPhenotypicFeatureAssociation')
      AND predicate = 'biolink:has_phenotype' AND (negated IS NULL OR negated = 'False')""")
print("slim nodes (id, name) ...", flush=True)
con.execute("CREATE TABLE nodes AS SELECT id, name FROM s.nodes")

print("bake ducksim_ic ...", flush=True)
con.execute(f"""CREATE TABLE ducksim_ic AS
    WITH clo AS (SELECT object_id AS o FROM closure),
         n   AS (SELECT count(DISTINCT o) AS nn FROM clo)
    SELECT o AS term, -log2(count(*)::DOUBLE / (SELECT nn FROM n)) AS ic FROM clo GROUP BY o""")
print("bake ducksim_esize ...", flush=True)
con.execute("""CREATE TABLE ducksim_esize AS
    SELECT e.subject AS entity, count(DISTINCT c.object_id) AS pn
    FROM edges e JOIN closure c ON c.subject_id = e.object GROUP BY e.subject""")

con.execute("DETACH s")
for t in ("closure", "edges", "nodes", "ducksim_ic", "ducksim_esize"):
    print(f"  {t:14} {con.execute(f'SELECT count(*) FROM {t}').fetchone()[0]:>12,}")
con.close()
print("done:", out)
