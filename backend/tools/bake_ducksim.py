#!/usr/bin/env python3
"""Bake ducksim's precomputed tables into a copy of monarch-kg.duckdb.

Adds two small tables — `ducksim_ic` (term -> IC) and `ducksim_esize` (entity -> |phenotype
closure|) — that the ducksim engine reads instead of building at startup. This removes the
per-worker fan-out build (the main memory spike on the api VM). One-off for now; the same SQL
should eventually move into the monarch-ingest build.

The SQL here MUST match the engine's runtime build (service/ducksim.py): IC over the
rdfs:subClassOf closure, esize over Gene/Disease has_phenotype associations.

Usage:  python3 bake_ducksim.py IN.duckdb OUT.duckdb
"""
import shutil
import sys

import duckdb

src, out = sys.argv[1], sys.argv[2]
print(f"copying {src} -> {out} ...", flush=True)
shutil.copy(src, out)

con = duckdb.connect(out)  # read-write
print("building ducksim_ic ...", flush=True)
con.execute("""
    CREATE TABLE ducksim_ic AS
    WITH clo AS (SELECT object_id AS o FROM closure WHERE predicate_id = 'rdfs:subClassOf'),
         n   AS (SELECT count(DISTINCT o) AS nn FROM clo)
    SELECT o AS term, -log2(count(*)::DOUBLE / (SELECT nn FROM n)) AS ic
    FROM clo GROUP BY o
""")
print("building ducksim_esize ...", flush=True)
con.execute("""
    CREATE TABLE ducksim_esize AS
    WITH assoc AS (
        SELECT subject AS entity, object AS phenotype FROM edges
        WHERE category IN ('biolink:GeneToPhenotypicFeatureAssociation',
                           'biolink:DiseaseToPhenotypicFeatureAssociation')
          AND predicate = 'biolink:has_phenotype' AND (negated IS NULL OR negated = 'False')),
         clo AS (SELECT subject_id AS s, object_id AS o FROM closure WHERE predicate_id = 'rdfs:subClassOf')
    SELECT a.entity, count(DISTINCT c.o) AS pn
    FROM assoc a JOIN clo c ON c.s = a.phenotype GROUP BY a.entity
""")
print("ducksim_ic rows   :", con.execute("SELECT count(*) FROM ducksim_ic").fetchone()[0])
print("ducksim_esize rows:", con.execute("SELECT count(*) FROM ducksim_esize").fetchone()[0])
con.close()
print("done:", out)
