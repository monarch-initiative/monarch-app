"""Evaluate phenotype search ranking settings on simulated patients.

Runs against a local monarch-kg.duckdb (download it from
https://data.monarchinitiative.org/monarch-kg/latest/monarch-kg.duckdb). See
`monarch_py.utils.semsim_eval` for the query kinds, noise models and what is reported.

Each full search over all diseases takes a few seconds, so a run costs roughly
sample x query kinds x noise models x settings x 3 s. The defaults (50 diseases, 3 kinds,
no noise, 6 settings) take about 45 minutes.

Examples:
    cd backend
    uv run python ../scripts/semsim_eval.py --kg /data/monarch-kg.duckdb --out eval/
    uv run python ../scripts/semsim_eval.py --kg /data/monarch-kg.duckdb --noise none parent unrelated \\
        --configs production query_to_entity_frequency --sample 100 --out eval/
    uv run python ../scripts/semsim_eval.py --kg /data/monarch-kg.duckdb --target HGNC --out eval-genes/
"""

import argparse
import csv
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
    format_summary,
    rows_as_dicts,
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
    )
    started = time.time()

    def progress(done, total):
        print(f"{done}/{total} diseases, {time.time() - started:.0f}s", file=sys.stderr, flush=True)

    rows = SemsimEvaluation(engine, options).run(progress=progress)
    args.out.mkdir(parents=True, exist_ok=True)
    records = rows_as_dicts(rows)
    with open(args.out / "results.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]) if records else [])
        writer.writeheader()
        writer.writerows(records)
    table = format_summary(summarize(rows))
    (args.out / "summary.md").write_text(table + "\n")
    print(table)


if __name__ == "__main__":
    main()
