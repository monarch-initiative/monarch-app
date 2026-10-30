"""Simulated-patient evaluation of phenotype search ranking settings.

Each simulated patient is a set of phenotype terms drawn from one disease's annotations. The
harness searches with that query under several ranking settings and records where the right answer
lands: the disease itself when searching diseases, or the genes that cause it when searching genes.
It runs on a `monarch-kg.duckdb` through `Ducksim` directly, with no API server.

Query kinds (built from the disease's own annotations):
  random            `query_size` terms sampled uniformly
  random_weighted   `query_size` terms sampled in proportion to their recorded frequency in the
                    disease (missing frequencies count as Ducksim's DEFAULT_FREQUENCY), the way
                    patients present
  common_rare       the disease's `common_count` most widely annotated terms plus its rarest one
  rare_alone        the disease's rarest term (fewest annotated diseases in the corpus)
When several terms tie for rarest, one is picked at random (seeded). Ties among the most common
terms are broken by CURIE.

Noise models, applied on top of a query kind:
  none            the terms as drawn
  parent          each term replaced by one of its direct parents with probability `parent_rate`,
                  the way clinicians often record a broader term
  other_disease   `other_disease_count` terms added from other diseases' profiles. Only the
                  disease's exact terms are excluded, so an added term can still be an ancestor or
                  descendant of one of them and match partially.

Every noise model is applied to the same base query for a disease and kind, so the noise columns
compare like with like. Each (disease, kind) and (disease, kind, noise) draws from its own seeded
generator, so a query does not change when other kinds, noise models or settings are added to a run.

Exact profile terms flatter every setting, because no other entity can outscore an exact match.
The noise models are where information content and the tie-break are expected to matter.

Gene targets are optimistic. Monarch's human gene-to-phenotype edges come from HPO's
genes_to_phenotype, which HPO derives from the disease annotations, so a causal gene's profile
already contains the disease's terms. Read `--target HGNC` results as an upper bound.

What is reported per query and setting:
  position   where the answer appears in the ranked list a user sees (None if absent). Hybrid
             search returns only `hybrid_limit` results, as production does. Without a tie-break,
             equal scores are ordered by id, which is arbitrary, so read position with tie_size.
  tie_size   how many entities share the answer's score, itself included (full search only). For
             the frequency tie-break settings this still counts equal scores, not the entities left
             tied after the tie-break, so there the position is no longer arbitrary.
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import asdict, dataclass, field
from typing import Dict, Iterable, Iterator, List, Optional

from monarch_py.service.ducksim import DEFAULT_FREQUENCY, MIN_FREQUENCY, Ducksim

# Ranking settings to compare. "production" is today's default.
CONFIGS: Dict[str, dict] = {
    "production": dict(mode="hybrid", direction="bidirectional", information_content="ontology", tie_break="none"),
    "full": dict(mode="full", direction="bidirectional", information_content="ontology", tie_break="none"),
    "full_annotation_ic": dict(
        mode="full", direction="bidirectional", information_content="annotation", tie_break="none"
    ),
    "query_to_entity": dict(
        mode="full", direction="object_to_subject", information_content="ontology", tie_break="none"
    ),
    "query_to_entity_frequency": dict(
        mode="full", direction="object_to_subject", information_content="ontology", tie_break="frequency"
    ),
    "query_to_entity_annotation_ic_frequency": dict(
        mode="full", direction="object_to_subject", information_content="annotation", tie_break="frequency"
    ),
}
QUERY_KINDS = ("random", "random_weighted", "common_rare", "rare_alone")
NOISE_MODELS = ("none", "parent", "other_disease")
# How many other diseases the other_disease noise draws its pool of terms from.
OTHER_DISEASE_POOL = 50


@dataclass
class EvalOptions:
    target_prefix: str = "MONDO"  # MONDO: find the disease; HGNC: find a gene that causes it
    sample: int = 50
    seed: int = 0
    min_terms: int = 10
    query_size: int = 5
    common_count: int = 4
    kinds: List[str] = field(default_factory=lambda: list(QUERY_KINDS))
    noise: List[str] = field(default_factory=lambda: ["none"])
    configs: List[str] = field(default_factory=lambda: list(CONFIGS))
    parent_rate: float = 0.5
    other_disease_count: int = 2
    hybrid_limit: int = 10


@dataclass
class EvalRow:
    disease: str
    kind: str
    noise: str
    config: str
    query: str
    answers: str
    position: Optional[int]
    tie_size: Optional[int]
    answer_score: Optional[float]


class SemsimEvaluation:
    """Builds simulated patients from the KG and ranks them under each setting."""

    def __init__(self, engine: Ducksim, options: EvalOptions):
        self.engine = engine
        self.options = options
        # MONDO disease -> its non-negated HP annotations (the source of every simulated patient)
        self.profiles = engine.annotations_by_prefix("MONDO", phenotype_prefix="HP")
        self.term_counts = self._annotated_entity_counts()
        self.parents = engine.direct_parents("HP")
        self.answers = self._answers()
        self._base_queries: Dict[tuple, List[str]] = {}

    # ---- data -----------------------------------------------------------

    def _annotated_entity_counts(self) -> Dict[str, int]:
        """HP term -> number of diseases annotated to it directly. "Rare" and "common" use this."""
        counts: Dict[str, int] = {}
        for terms in self.profiles.values():
            for term in terms:
                counts[term] = counts.get(term, 0) + 1
        return counts

    def _answers(self) -> Dict[str, List[str]]:
        """Disease -> the entities that count as a correct answer for a patient with it."""
        if self.options.target_prefix == "MONDO":
            return {disease: [disease] for disease in self.profiles}
        return self.engine.causal_genes_by_disease(self.options.target_prefix)

    def _rng(self, *parts) -> random.Random:
        return random.Random(":".join(str(p) for p in (self.options.seed, *parts)))

    # ---- queries --------------------------------------------------------

    def sample_diseases(self) -> List[str]:
        eligible = sorted(
            disease
            for disease, terms in self.profiles.items()
            if len(terms) >= self.options.min_terms and self.answers.get(disease)
        )
        return self._rng("sample").sample(eligible, min(self.options.sample, len(eligible)))

    def base_query(self, disease: str, kind: str) -> List[str]:
        """The query before noise. The same for every noise model applied to it."""
        key = (disease, kind)
        if key not in self._base_queries:
            self._base_queries[key] = self._draw_base_query(disease, kind, self._rng(disease, kind))
        return list(self._base_queries[key])

    def _draw_base_query(self, disease: str, kind: str, rng: random.Random) -> List[str]:
        profile = self.profiles[disease]
        if kind == "random":
            return rng.sample(profile, min(self.options.query_size, len(profile)))
        if kind == "random_weighted":
            return self._frequency_weighted_sample(disease, profile, rng)
        if kind not in ("common_rare", "rare_alone"):
            raise ValueError(f"unknown query kind {kind!r}")
        fewest = min(self.term_counts[t] for t in profile)
        rarest = rng.choice([t for t in profile if self.term_counts[t] == fewest])
        if kind == "rare_alone":
            return [rarest]
        by_commonness = sorted((t for t in profile if t != rarest), key=lambda t: (-self.term_counts[t], t))
        return by_commonness[: self.options.common_count] + [rarest]

    def build_query(self, disease: str, kind: str, noise: str) -> List[str]:
        terms = self.base_query(disease, kind)
        rng = self._rng(disease, kind, noise)
        if noise == "parent":
            terms = [
                rng.choice(self.parents[t]) if self.parents.get(t) and rng.random() < self.options.parent_rate else t
                for t in terms
            ]
        elif noise == "other_disease":
            others = [d for d in self.profiles if d != disease]
            pool = {t for d in rng.sample(others, min(OTHER_DISEASE_POOL, len(others))) for t in self.profiles[d]}
            pool -= set(self.profiles[disease])
            terms = terms + rng.sample(sorted(pool), min(self.options.other_disease_count, len(pool)))
        elif noise != "none":
            raise ValueError(f"unknown noise model {noise!r}")
        return list(dict.fromkeys(terms))

    def _frequency_weighted_sample(self, disease: str, profile: List[str], rng: random.Random) -> List[str]:
        """Sample without replacement, each term weighted by its recorded frequency in the disease,
        floored at MIN_FREQUENCY as the tie-break does, so a term recorded in 0 patients is unlikely
        but possible."""
        freq = self.engine.frequencies_batch([disease])
        remaining = list(profile)
        chosen: List[str] = []
        while remaining and len(chosen) < self.options.query_size:
            weights = [max(MIN_FREQUENCY, freq.get((disease, term), DEFAULT_FREQUENCY)) for term in remaining]
            pick = rng.choices(remaining, weights=weights, k=1)[0]
            chosen.append(pick)
            remaining.remove(pick)
        return chosen

    # ---- ranking --------------------------------------------------------

    def rank(self, query: List[str], answers: List[str], config: dict):
        """(position, tie_size, score) of the best-placed answer under one setting."""
        prefix = self.options.target_prefix
        kwargs = dict(
            prefix=prefix,
            direction=config["direction"],
            information_content=config["information_content"],
            tie_break=config["tie_break"],
        )
        if config["mode"] == "hybrid":
            ranked = self.engine.hybrid_search(query, limit=self.options.hybrid_limit, **kwargs)
        else:
            ranked = self.engine.full_search(query, limit=None, **kwargs)
        order = [entity for entity, _ in ranked]
        scores = {entity: round(score, 9) for entity, score in ranked}
        found = [order.index(a) for a in answers if a in scores]
        if not found:
            return None, None, None
        best = order[min(found)]
        tie_size = sum(1 for s in scores.values() if s == scores[best]) if config["mode"] == "full" else None
        return min(found) + 1, tie_size, scores[best]

    def iter_rows(self, progress=None) -> Iterator[List[EvalRow]]:
        """The rows for each sampled disease in turn, so a caller can save them as it goes."""
        diseases = self.sample_diseases()
        for i, disease in enumerate(diseases):
            answers = self.answers[disease]
            rows: List[EvalRow] = []
            for kind in self.options.kinds:
                for noise in self.options.noise:
                    query = self.build_query(disease, kind, noise)
                    for name in self.options.configs:
                        position, tie_size, score = self.rank(query, answers, CONFIGS[name])
                        rows.append(
                            EvalRow(
                                disease=disease,
                                kind=kind,
                                noise=noise,
                                config=name,
                                query=",".join(query),
                                answers=",".join(answers),
                                position=position,
                                tie_size=tie_size,
                                answer_score=score,
                            )
                        )
            yield rows
            if progress:
                progress(i + 1, len(diseases))

    def run(self, progress=None) -> List[EvalRow]:
        return [row for rows in self.iter_rows(progress) for row in rows]


def summarize(rows: Iterable[EvalRow], depth: int = 10) -> List[dict]:
    """Per (query kind, noise, setting): hit rates, mean reciprocal rank, median position and tie size.

    MRR and median position count only answers within `depth`, so hybrid search (which returns at
    most `hybrid_limit` results) and full search are cut at the same place. Pass the hybrid limit."""
    groups: Dict[tuple, List[EvalRow]] = {}
    for row in rows:
        groups.setdefault((row.kind, row.noise, row.config), []).append(row)
    summary = []
    for (kind, noise, config), group in groups.items():
        positions = [r.position if r.position is not None and r.position <= depth else None for r in group]
        ties = [r.tie_size for r in group if r.tie_size is not None]
        summary.append(
            {
                "kind": kind,
                "noise": noise,
                "config": config,
                "n": len(group),
                "depth": depth,
                "top1": sum(1 for p in positions if p == 1) / len(group),
                "top10": sum(1 for r in group if r.position is not None and r.position <= 10) / len(group),
                "mrr": sum(1 / p for p in positions if p) / len(group),
                "median_position": statistics.median([p if p is not None else math.inf for p in positions]),
                "median_tie_size": statistics.median(ties) if ties else None,
            }
        )
    return sorted(summary, key=lambda s: (s["kind"], s["noise"], s["config"]))


def format_summary(summary: List[dict]) -> str:
    """A markdown table of `summarize` output."""
    depth = summary[0]["depth"] if summary else 10
    lines = [
        f"| query | noise | setting | n | top 1 | top 10 | MRR@{depth} | median position | median tie size |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for s in summary:
        tie = "" if s["median_tie_size"] is None else f"{s['median_tie_size']:g}"
        median = f">{depth}" if math.isinf(s["median_position"]) else f"{s['median_position']:g}"
        lines.append(
            f"| {s['kind']} | {s['noise']} | {s['config']} | {s['n']} | {s['top1']:.0%} | {s['top10']:.0%} "
            f"| {s['mrr']:.3f} | {median} | {tie} |"
        )
    return "\n".join(lines)


def rows_as_dicts(rows: Iterable[EvalRow]) -> List[dict]:
    return [asdict(row) for row in rows]


__all__ = [
    "CONFIGS",
    "NOISE_MODELS",
    "QUERY_KINDS",
    "EvalOptions",
    "EvalRow",
    "SemsimEvaluation",
    "format_summary",
    "rows_as_dicts",
    "summarize",
]
