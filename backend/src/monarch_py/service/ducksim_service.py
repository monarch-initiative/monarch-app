"""DucksimService — drop-in for SemsimianService backed by the in-process DuckDB engine.

Implements the same `compare` / `multi_compare` / `search` interface and returns the same pydantic
models, but computes everything against the read-only monarch-kg.duckdb instead of calling the
semsimian HTTP server. See `monarch_py/service/ducksim.py` for the engine.
"""

from typing import Any, List, Optional

from monarch_py.api.additional_models import (
    SemsimDirectionality,
    SemsimMetric,
    SemsimInformationContent,
    SemsimMultiCompareRequest,
    SemsimSearchMode,
    SemsimTieBreak,
    DEFAULT_FREQUENCY,
)
from monarch_py.datamodels.model import (
    BestMatch,
    Entity,
    SemsimSearchResult,
    TermInfo,
    TermPairwiseSimilarity,
    TermSetPairwiseSimilarity,
)
from monarch_py.service.curie_service import converter
from monarch_py.service.ducksim import Ducksim


class DucksimService:
    """Semantic-similarity service computed in DuckDB (semsimian-equivalent)."""

    def __init__(self, engine: Ducksim, entity_implementation: Any = None):
        self.engine = engine
        # Retained for interface parity with SemsimianService; the DuckDB backend hydrates result
        # entities from the KG `nodes` table itself (see `_hydrate`), so it needs no external store.
        self.entity_implementation = entity_implementation

    # ---- compare --------------------------------------------------------

    def compare(
        self,
        subjects: List[str],
        objects: List[str],
        metric: SemsimMetric = SemsimMetric.ANCESTOR_INFORMATION_CONTENT,
        information_content: SemsimInformationContent = SemsimInformationContent.ONTOLOGY,
        group_prefix: Optional[str] = None,
        directionality: SemsimDirectionality = SemsimDirectionality.BIDIRECTIONAL,
    ) -> TermSetPairwiseSimilarity:
        """`group_prefix` (e.g. "MONDO") picks the annotation corpus when information_content is
        annotation; ontology IC ignores it. `directionality` picks which best matches
        `average_score` averages."""
        result = self.engine.termset_pairwise_similarity(
            subjects,
            objects,
            str(metric),
            direction=SemsimDirectionality(directionality).value,
            information_content=str(information_content),
            corpus_prefix=group_prefix,
        )
        lab = self.engine.labels(self._referenced_ids(result))
        return self._to_model(result, lab)

    def multi_compare(
        self, request: SemsimMultiCompareRequest, group_prefix: Optional[str] = None
    ) -> List[SemsimSearchResult]:
        results = []
        for object_set in request.object_sets:
            comparison = self.compare(
                request.subjects,
                object_set.phenotypes,
                request.metric,
                information_content=request.information_content,
                group_prefix=group_prefix,
                directionality=request.directionality,
            )
            results.append(
                SemsimSearchResult(
                    subject=Entity(id=object_set.id, name=object_set.label),
                    score=comparison.average_score,
                    similarity=comparison,
                )
            )
        return results

    # ---- search ---------------------------------------------------------

    def search(
        self,
        termset: List[str],
        prefix: str,
        metric: SemsimMetric = SemsimMetric.ANCESTOR_INFORMATION_CONTENT,
        directionality: SemsimDirectionality = SemsimDirectionality.BIDIRECTIONAL,
        limit: int = 10,
        search_mode: SemsimSearchMode = SemsimSearchMode.HYBRID,
        information_content: SemsimInformationContent = SemsimInformationContent.ONTOLOGY,
        tie_break: SemsimTieBreak = SemsimTieBreak.NONE,
        default_frequency: float = DEFAULT_FREQUENCY,
    ) -> List[SemsimSearchResult]:
        # Hybrid (the default) matches the semsimian server. Full scores every entity in the group,
        # so a richly annotated entity can't be dropped by hybrid's Jaccard prefilter (see engine).
        # The engine ranks and enriches the whole page in a constant number of DuckDB queries (no
        # per-result round-trips); the loop below is pure in-memory model shaping.
        direction = directionality.value if hasattr(directionality, "value") else str(directionality)
        page = self.engine.search(
            termset,
            limit=limit,
            metric=str(metric),
            prefix=prefix,
            direction=direction,
            mode=str(search_mode),
            information_content=str(information_content),
            tie_break=str(tie_break),
            default_frequency=default_frequency,
        )
        if not page:
            return []
        # all-DuckDB hydration of result entities from the KG `nodes` table — no external entity store
        entities = self.engine.entities([entity_id for entity_id, _, _ in page])
        # one label lookup for every id the whole page references
        ids = set()
        for _, _, comparison in page:
            ids |= self._referenced_ids(comparison)
        lab = self.engine.labels(ids)
        return [
            SemsimSearchResult(
                subject=self._hydrate(entities.get(entity_id), entity_id),
                score=score,
                similarity=self._to_model(comparison, lab),
            )
            for entity_id, score, comparison in page
        ]

    # ---- model shaping --------------------------------------------------

    def _hydrate(self, row: dict, entity_id: str) -> Entity:
        """Build a result Entity straight from the KG `nodes` row (all-DuckDB; no external store).
        Mirrors solr `parse_entity`: expand the curie to a uri and drop bulky descendant lists.
        Falls back to a bare id if the entity is somehow absent from `nodes`."""
        if not row:
            return Entity(id=entity_id)
        entity = Entity(**row)
        entity.uri = converter.expand(entity.id)
        entity.has_descendant = None
        entity.has_descendant_label = None
        return entity

    @staticmethod
    def _referenced_ids(r: dict) -> set:
        """Every term/entity id a comparison's model will reference (for one batched label lookup)."""
        ids = set(r["subject_termset"]) | set(r["object_termset"])
        for bm in list(r["subject_best_matches"].values()) + list(r["object_best_matches"].values()):
            ids.update(
                [
                    bm["match_target"],
                    bm["match_subsumer"],
                    bm["similarity"]["subject_id"],
                    bm["similarity"]["object_id"],
                ]
            )
        return {i for i in ids if i}

    def _to_model(self, r: dict, lab: dict) -> TermSetPairwiseSimilarity:
        def best_match(source: str, bm: dict) -> BestMatch:
            sim = bm["similarity"]
            return BestMatch(
                match_source=source,
                match_source_label=lab.get(source),
                match_target=bm["match_target"],
                match_target_label=lab.get(bm["match_target"]),
                score=bm["score"],
                frequency=bm.get("frequency"),
                match_subsumer=bm["match_subsumer"],
                match_subsumer_label=lab.get(bm["match_subsumer"]),
                similarity=TermPairwiseSimilarity(
                    subject_id=sim["subject_id"],
                    subject_label=lab.get(sim["subject_id"]),
                    object_id=sim["object_id"],
                    object_label=lab.get(sim["object_id"]),
                    ancestor_id=sim["ancestor_id"],
                    ancestor_label=lab.get(sim["ancestor_id"]),
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
            average_score=r["average_score"],
            best_score=r["best_score"],
            metric=r["metric"],
        )
