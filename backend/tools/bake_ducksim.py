#!/usr/bin/env python3
"""Bake a slim similarity DuckDB from monarch-kg.duckdb.

SUPERSEDED on the production path: the precompute tables (`information_content`,
`closure_size`) are now built into monarch-kg.duckdb itself by koza's
`information-content` operation during the KG build (monarch-ingest), and the api
reads them straight from the full KG artifact. This script is retained only as an
optional way to produce a *slim standalone* copy (e.g. for a smaller download
or local experiments).

The similarity engine touches just:
  closure (rdfs:subClassOf rows), edges (Gene/Disease has_phenotype), nodes (id,name).
So we build a slim copy with exactly those, plus the two precomputed tables the engine reads instead
of building at startup:
  information_content (term -> IC)            -- removes the per-worker IC build
  closure_size        (entity -> |closure|)  -- removes the per-worker fan-out build (the spike)

The SQL matches koza's `information-content` and the engine's runtime build (service/ducksim.py).

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

print("bake information_content ...", flush=True)
con.execute(f"""CREATE TABLE information_content AS
    WITH clo AS (SELECT object_id AS o FROM closure),
         n   AS (SELECT count(DISTINCT o) AS nn FROM clo)
    SELECT o AS term, -log2(count(*)::DOUBLE / (SELECT nn FROM n)) AS ic FROM clo GROUP BY o""")
print("bake closure_size ...", flush=True)
con.execute("""CREATE TABLE closure_size AS
    SELECT e.subject AS entity, count(DISTINCT c.object_id) AS size
    FROM edges e JOIN closure c ON c.subject_id = e.object GROUP BY e.subject""")

con.execute("DETACH s")
for t in ("closure", "edges", "nodes", "information_content", "closure_size"):
    print(f"  {t:14} {con.execute(f'SELECT count(*) FROM {t}').fetchone()[0]:>12,}")
con.close()
print("done:", out)
