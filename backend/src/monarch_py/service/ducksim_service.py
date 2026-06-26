"""DucksimService — drop-in for SemsimianService backed by the in-process DuckDB engine.

Implements the same `compare` / `multi_compare` / `search` interface and returns the same pydantic
models, but computes everything against the read-only monarch-kg.duckdb instead of calling the
semsimian HTTP server. See `monarch_py/service/ducksim.py` for the engine.
"""

from typing import Any, List

from monarch_py.api.additional_models import SemsimDirectionality, SemsimMetric, SemsimMultiCompareRequest
from monarch_py.datamodels.model import (
    BestMatch,
    Entity,
    SemsimSearchResult,
    TermInfo,
    TermPairwiseSimilarity,
    TermSetPairwiseSimilarity,
)
from monarch_py.service.ducksim import Ducksim


class DucksimService:
    """Semantic-similarity service computed in DuckDB (semsimian-equivalent)."""

    def __init__(self, engine: Ducksim, entity_implementation: Any):
        self.engine = engine
        self.entity_implementation = entity_implementation  # for hydrating search-result entities

    # ---- compare --------------------------------------------------------

    def compare(
        self, subjects: List[str], objects: List[str],
        metric: SemsimMetric = SemsimMetric.ANCESTOR_INFORMATION_CONTENT,
    ) -> TermSetPairwiseSimilarity:
        result = self.engine.termset_pairwise_similarity(subjects, objects, str(metric))
        return self._to_model(result)

    def multi_compare(self, request: SemsimMultiCompareRequest) -> List[SemsimSearchResult]:
        results = []
        for object_set in request.object_sets:
            comparison = self.compare(request.subjects, object_set.phenotypes, request.metric)
            results.append(SemsimSearchResult(
                subject=Entity(id=object_set.id, name=object_set.label),
                score=comparison.average_score,
                similarity=comparison,
            ))
        return results

    # ---- search ---------------------------------------------------------

    def search(
        self,
        termset: List[str],
        prefix: str,
        metric: SemsimMetric = SemsimMetric.ANCESTOR_INFORMATION_CONTENT,
        directionality: SemsimDirectionality = SemsimDirectionality.BIDIRECTIONAL,
        limit: int = 10,
    ) -> List[SemsimSearchResult]:
        # Hybrid mode matches the semsimian server; full_search would be more accurate (see engine).
        direction = directionality.value if hasattr(directionality, "value") else str(directionality)
        ranked = self.engine.hybrid_search(
            termset, limit=limit, metric=str(metric), prefix=prefix, direction=direction)
        results = []
        for entity_id, score in ranked:
            # entity phenotypes are the subjects, the query termset the objects — same orientation as
            # the ranking, so `direction` makes similarity.average_score match the ranked `score`.
            comparison = self.engine.termset_pairwise_similarity(
                self.engine.entity_phenotypes(entity_id), termset, str(metric), direction=direction)
            results.append(SemsimSearchResult(
                subject=self.entity_implementation.get_entity(entity_id, extra=False),
                score=score,
                similarity=self._to_model(comparison),
            ))
        return results

    # ---- model shaping --------------------------------------------------

    def _to_model(self, r: dict) -> TermSetPairwiseSimilarity:
        # one label lookup for every id the model references
        ids = set(r["subject_termset"]) | set(r["object_termset"])
        for bm in list(r["subject_best_matches"].values()) + list(r["object_best_matches"].values()):
            ids.update([bm["match_target"], bm["match_subsumer"],
                        bm["similarity"]["subject_id"], bm["similarity"]["object_id"]])
        lab = self.engine.labels(ids)

        def best_match(source: str, bm: dict) -> BestMatch:
            sim = bm["similarity"]
            return BestMatch(
                match_source=source, match_source_label=lab.get(source),
                match_target=bm["match_target"], match_target_label=lab.get(bm["match_target"]),
                score=bm["score"],
                match_subsumer=bm["match_subsumer"], match_subsumer_label=lab.get(bm["match_subsumer"]),
                similarity=TermPairwiseSimilarity(
                    subject_id=sim["subject_id"], subject_label=lab.get(sim["subject_id"]),
                    object_id=sim["object_id"], object_label=lab.get(sim["object_id"]),
                    ancestor_id=sim["ancestor_id"], ancestor_label=lab.get(sim["ancestor_id"]),
                    # metric scores ride through as extra fields (model allows extra)
                    jaccard_similarity=sim["jaccard_similarity"],
                    ancestor_information_content=sim["ancestor_information_content"],
                    phenodigm_score=sim["phenodigm_score"],
                ),
            )

        return TermSetPairwiseSimilarity(
            subject_termset={i: TermInfo(id=i, label=lab.get(i)) for i in r["subject_termset"]},
            object_termset={i: TermInfo(id=i, label=lab.get(i)) for i in r["object_termset"]},
            subject_best_matches={s: best_match(s, bm) for s, bm in r["subject_best_matches"].items()},
            object_best_matches={o: best_match(o, bm) for o, bm in r["object_best_matches"].items()},
            average_score=r["average_score"], best_score=r["best_score"], metric=r["metric"],
        )
