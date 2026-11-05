"""Evaluate phenotype search ranking settings on simulated patients.

Runs against a local monarch-kg.duckdb (download it from
https://data.monarchinitiative.org/monarch-kg/latest/monarch-kg.duckdb). See
`monarch_py.utils.semsim_eval` for the query kinds, noise models and what is reported.
Gene-target results (`--target HGNC`) are an upper bound: see that module's docstring.

Each full search over all diseases takes a few seconds, so a run costs roughly
sample x query kinds x noise models x settings x 3 s. The defaults (50 diseases, 4 kinds,
no noise, 6 settings) take about an hour. results.csv is written as each disease finishes, so an
interrupted run keeps what it has; summary.md is written at the end.

Examples:
    cd backend
    uv run python ../scripts/semsim_eval.py --kg /data/monarch-kg.duckdb --out eval/
    uv run python ../scripts/semsim_eval.py --kg /data/monarch-kg.duckdb --noise none parent other_disease \\
        --configs production query_to_entity_frequency --sample 100 --out eval/
    uv run python ../scripts/semsim_eval.py --kg /data/monarch-kg.duckdb --target HGNC --out eval-genes/
"""

import argparse
import csv
import dataclasses
import sys
import time
from pathlib import Path

from monarch_py.service.ducksim import Ducksim
from monarch_py.utils.semsim_eval import (
    CONFIGS,
    NOISE_MODELS,
    QUERY_KINDS,
    EvalOptions,
    SemsimEvaluation,
    EvalRow,
    format_summary,
    summarize,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--kg", required=True, help="path to monarch-kg.duckdb")
    parser.add_argument("--out", required=True, type=Path, help="directory for results.csv and summary.md")
    parser.add_argument("--target", default="MONDO", help="MONDO (find the disease) or a gene prefix such as HGNC")
    parser.add_argument("--sample", type=int, default=50, help="number of diseases to simulate patients for")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--min-terms", type=int, default=10, help="only diseases with at least this many annotations")
    parser.add_argument("--kinds", nargs="+", default=list(QUERY_KINDS), choices=QUERY_KINDS)
    parser.add_argument("--noise", nargs="+", default=["none"], choices=NOISE_MODELS)
    parser.add_argument("--configs", nargs="+", default=list(CONFIGS), choices=list(CONFIGS))
    parser.add_argument("--query-size", type=int, default=5, help="terms in a random or random_weighted query")
    parser.add_argument("--common-count", type=int, default=4, help="common terms in a common_rare query")
    parser.add_argument("--parent-rate", type=float, default=0.5, help="chance each term is replaced by a parent")
    parser.add_argument("--other-disease-count", type=int, default=2, help="terms added by other_disease noise")
    parser.add_argument(
        "--hybrid-limit", type=int, default=10, help="results hybrid search returns; also the MRR and median depth"
    )
    parser.add_argument("--memory-limit", default="8GB")
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args(argv)

    engine = Ducksim.from_duckdb(args.kg, memory_limit=args.memory_limit, threads=args.threads)
    if any(CONFIGS[c]["information_content"] == "annotation" for c in args.configs):
        if args.target not in engine.annotation_ic_views:
            parser.error(f"this KG has no annotation-IC table for {args.target}; drop the annotation-IC settings")
    options = EvalOptions(
        target_prefix=args.target,
        sample=args.sample,
        seed=args.seed,
        min_terms=args.min_terms,
        kinds=args.kinds,
        noise=args.noise,
        configs=args.configs,
        query_size=args.query_size,
        common_count=args.common_count,
        parent_rate=args.parent_rate,
        other_disease_count=args.other_disease_count,
        hybrid_limit=args.hybrid_limit,
    )
    started = time.time()

    def progress(done, total):
        print(f"{done}/{total} diseases, {time.time() - started:.0f}s", file=sys.stderr, flush=True)

    args.out.mkdir(parents=True, exist_ok=True)
    rows = []
    with open(args.out / "results.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[f.name for f in dataclasses.fields(EvalRow)])
        writer.writeheader()
        for disease_rows in SemsimEvaluation(engine, options).iter_rows(progress=progress):
            writer.writerows(dataclasses.asdict(row) for row in disease_rows)
            handle.flush()
            rows.extend(disease_rows)
    table = format_summary(summarize(rows, depth=args.hybrid_limit))
    if args.target != "MONDO":
        table = (
            f"Gene target {args.target}: these results are an upper bound. The genes' phenotype edges are "
            "derived from the disease annotations the queries are drawn from.\n\n" + table
        )
    (args.out / "summary.md").write_text(table + "\n")
    print(table)


if __name__ == "__main__":
    main()
