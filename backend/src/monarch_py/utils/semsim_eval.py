"""Simulated-patient evaluation of phenotype search ranking settings.

Each simulated patient is a set of phenotype terms drawn from one disease's annotations. The
harness searches with that query under several ranking settings and records where the right answer
lands: the disease itself when searching diseases, or the genes that cause it when searching genes.
It runs on a `monarch-kg.duckdb` through `Ducksim` directly, with no API server.

Query kinds (built from the disease's own annotations):
  random       `query_size` terms sampled uniformly
  common_rare  the disease's most widely annotated terms plus its rarest one
  rare_alone   the disease's rarest term (fewest annotated entities in the corpus)

Noise models, applied on top of a query kind:
  none                 the terms as drawn
  parent               each term replaced by one of its direct parents with probability
                       `parent_rate`, the way clinicians often record a broader term
  unrelated            `unrelated_count` terms from other diseases added
  frequency_weighted   for `random`, terms sampled in proportion to their recorded frequency in the
                       disease (missing frequencies count as 0.5), the way patients present

Exact profile terms flatter every setting, because no other entity can outscore an exact match.
The noise models are where information content and the tie-break are expected to matter.

What is reported per query and setting:
  position   where the answer appears in the ranked list a user sees (None if absent). Hybrid
             search returns only `hybrid_limit` results, as production does. Without a tie-break,
             equal scores are ordered by id, which is arbitrary, so read position with tie_size.
  tie_size   how many entities share the answer's score, itself included (full search only)
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import asdict, dataclass, field
from typing import Dict, Iterable, List, Optional

from monarch_py.service.ducksim import Ducksim

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
QUERY_KINDS = ("random", "common_rare", "rare_alone")
NOISE_MODELS = ("none", "parent", "unrelated", "frequency_weighted")
CAUSAL_GENE_SQL = (
    "SELECT DISTINCT subject AS gene, object AS disease FROM src.edges "
    "WHERE category = 'biolink:CausalGeneToDiseaseAssociation' AND predicate = 'biolink:causes'"
)


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
    unrelated_count: int = 2
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
        self.rng = random.Random(options.seed)
        self.profiles = self._disease_profiles()
        self.term_counts = self._annotated_entity_counts()
        self.parents = self._direct_parents()
        self.answers = self._answers()

    # ---- data -----------------------------------------------------------

    def _rows(self, sql: str):
        return self.engine._read(sql).fetchall()

    def _disease_profiles(self) -> Dict[str, List[str]]:
        """MONDO disease -> its non-negated HP annotations (the source of every simulated patient)."""
        profiles: Dict[str, List[str]] = {}
        for entity, phenotype in self._rows(
            "SELECT DISTINCT entity, phenotype FROM _assoc "
            "WHERE entity LIKE 'MONDO:%' AND phenotype LIKE 'HP:%' ORDER BY entity, phenotype"
        ):
            profiles.setdefault(entity, []).append(phenotype)
        return profiles

    def _annotated_entity_counts(self) -> Dict[str, int]:
        """HP term -> number of diseases annotated to it directly. "Rare" and "common" use this."""
        counts: Dict[str, int] = {}
        for terms in self.profiles.values():
            for term in terms:
                counts[term] = counts.get(term, 0) + 1
        return counts

    def _direct_parents(self) -> Dict[str, List[str]]:
        parents: Dict[str, List[str]] = {}
        for child, parent in self._rows(
            "SELECT DISTINCT subject, object FROM src.edges WHERE predicate = 'biolink:subclass_of' "
            "AND subject LIKE 'HP:%' AND object LIKE 'HP:%' ORDER BY subject, object"
        ):
            parents.setdefault(child, []).append(parent)
        return parents

    def _answers(self) -> Dict[str, List[str]]:
        """Disease -> the entities that count as a correct answer for a patient with it."""
        if self.options.target_prefix == "MONDO":
            return {disease: [disease] for disease in self.profiles}
        prefix = self.options.target_prefix
        answers: Dict[str, List[str]] = {}
        for gene, disease in self._rows(f"{CAUSAL_GENE_SQL} ORDER BY gene"):
            if gene.split(":")[0] == prefix:
                answers.setdefault(disease, []).append(gene)
        return answers

    # ---- queries --------------------------------------------------------

    def sample_diseases(self) -> List[str]:
        eligible = sorted(
            disease
            for disease, terms in self.profiles.items()
            if len(terms) >= self.options.min_terms and self.answers.get(disease)
        )
        return self.rng.sample(eligible, min(self.options.sample, len(eligible)))

    def build_query(self, disease: str, kind: str, noise: str) -> List[str]:
        profile = self.profiles[disease]
        by_commonness = sorted(profile, key=lambda term: (-self.term_counts.get(term, 0), term))
        if kind == "random":
            if noise == "frequency_weighted":
                terms = self._frequency_weighted_sample(disease, profile)
            else:
                terms = self.rng.sample(profile, min(self.options.query_size, len(profile)))
        elif kind == "common_rare":
            terms = by_commonness[: self.options.common_count] + [by_commonness[-1]]
        elif kind == "rare_alone":
            terms = [by_commonness[-1]]
        else:
            raise ValueError(f"unknown query kind {kind!r}")
        if noise == "parent":
            terms = [
                self.rng.choice(self.parents[t])
                if self.parents.get(t) and self.rng.random() < self.options.parent_rate
                else t
                for t in terms
            ]
        elif noise == "unrelated":
            others = [d for d in self.profiles if d != disease]
            pool = {t for d in self.rng.sample(others, min(50, len(others))) for t in self.profiles[d]}
            pool -= set(profile)
            terms = terms + self.rng.sample(sorted(pool), min(self.options.unrelated_count, len(pool)))
        elif noise not in ("none", "frequency_weighted"):
            raise ValueError(f"unknown noise model {noise!r}")
        return list(dict.fromkeys(terms))

    def _frequency_weighted_sample(self, disease: str, profile: List[str]) -> List[str]:
        """Sample without replacement, each term weighted by its recorded frequency in the disease."""
        freq = self.engine.frequencies_batch([disease])
        remaining = list(profile)
        chosen: List[str] = []
        while remaining and len(chosen) < self.options.query_size:
            weights = [freq.get((disease, term), 0.5) for term in remaining]
            pick = self.rng.choices(remaining, weights=weights, k=1)[0]
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

    def run(self, progress=None) -> List[EvalRow]:
        rows: List[EvalRow] = []
        diseases = self.sample_diseases()
        for i, disease in enumerate(diseases):
            answers = self.answers[disease]
            for kind in self.options.kinds:
                for noise in self.options.noise:
                    if noise == "frequency_weighted" and kind != "random":
                        continue
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
            if progress:
                progress(i + 1, len(diseases))
        return rows


def summarize(rows: Iterable[EvalRow]) -> List[dict]:
    """Per (query kind, noise, setting): hit rates, mean reciprocal rank, median position and tie size."""
    groups: Dict[tuple, List[EvalRow]] = {}
    for row in rows:
        groups.setdefault((row.kind, row.noise, row.config), []).append(row)
    summary = []
    for (kind, noise, config), group in groups.items():
        positions = [r.position for r in group]
        ties = [r.tie_size for r in group if r.tie_size is not None]
        summary.append(
            {
                "kind": kind,
                "noise": noise,
                "config": config,
                "n": len(group),
                "top1": sum(1 for p in positions if p == 1) / len(group),
                "top10": sum(1 for p in positions if p is not None and p <= 10) / len(group),
                "mrr": sum(1 / p for p in positions if p) / len(group),
                "median_position": statistics.median([p if p is not None else math.inf for p in positions]),
                "median_tie_size": statistics.median(ties) if ties else None,
            }
        )
    return sorted(summary, key=lambda s: (s["kind"], s["noise"], s["config"]))


def format_summary(summary: List[dict]) -> str:
    """A markdown table of `summarize` output."""
    lines = [
        "| query | noise | setting | n | top 1 | top 10 | MRR | median position | median tie size |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for s in summary:
        tie = "" if s["median_tie_size"] is None else f"{s['median_tie_size']:g}"
        lines.append(
            f"| {s['kind']} | {s['noise']} | {s['config']} | {s['n']} | {s['top1']:.0%} | {s['top10']:.0%} "
            f"| {s['mrr']:.3f} | {s['median_position']:g} | {tie} |"
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
