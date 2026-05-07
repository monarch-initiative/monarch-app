"""Resolve per-source version info from the build receipt (metadata.yaml).

The receipt is a recursive `Release` (kozahub-metadata-schema): each ingest
declares the upstream sources it consumed, and aggregators (e.g. alliance-
ingest) may further nest per-component sub-sources (e.g. infores:zfin
inside infores:agr).

Two lookup paths consumers care about:

- Edge-level (aggregator-aware): given an edge's `aggregator_knowledge_source`
  and `primary_knowledge_source`, find the producing ingest, descend into its
  subtree, and look up the primary. Falls back to the aggregator's own
  version when the per-component sub-sources haven't been declared yet.

- Node-level (canonical): given an `infores:*`, return the version of the
  source-as-it-appears-in-the-merged-KG. Most ontology terms come through
  phenio (under kg-phenio); most data sources come from their self-named
  ingest (`infores:hgnc` → `hgnc-ingest`). The resolver picks one path per
  infores using that heuristic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

# `infores:monarchinitiative` always shows up as an aggregator on edges (we're
# the final aggregator). It carries no upstream-version information beyond
# the build's own date, so consumers strip it before edge resolution.
MONARCH_AGGREGATOR_INFORES = "infores:monarchinitiative"


@dataclass(frozen=True)
class SourceVersion:
    """A resolved version record for one (producer, infores) tuple."""

    infores: str
    name: str
    version: str
    version_method: str
    retrieved_at: str
    urls: tuple[str, ...]
    # Path of intermediate-build ids between the top-level ingest and this
    # entry, e.g. ("infores:agr",) when this is `infores:zfin` nested under
    # `infores:agr` in alliance-ingest's subtree. Empty tuple when this is
    # a direct child of the producer ingest.
    via: tuple[str, ...]


@dataclass(frozen=True)
class ResolvedReceipt:
    """An indexed view of one `metadata.yaml` document."""

    release: str
    generated_at: str
    # producer-ingest id -> infores -> SourceVersion
    by_producer: dict[str, dict[str, SourceVersion]]
    # infores -> producer-ingest id (the producer chosen as canonical for that
    # infores in node-level lookups). Built from the heuristic in
    # `_pick_canonical_producer`.
    canonical_producer: dict[str, str]
    disagreements: list[dict]
    version_drift: list[dict]


def index_receipt(receipt: dict) -> ResolvedReceipt:
    """Walk a parsed `metadata.yaml` and build the resolution index."""
    by_producer: dict[str, dict[str, SourceVersion]] = {}

    for ingest in receipt.get("sources") or []:
        ingest_id = ingest.get("id")
        if not ingest_id:
            continue
        flat: dict[str, SourceVersion] = {}
        _flatten_ingest(ingest, flat, via=())
        by_producer[ingest_id] = flat

    canonical_producer = _pick_canonical_producer(by_producer)

    return ResolvedReceipt(
        release=receipt.get("version") or "",
        generated_at=receipt.get("generated_at") or "",
        by_producer=by_producer,
        canonical_producer=canonical_producer,
        disagreements=list(receipt.get("disagreements") or []),
        version_drift=list(receipt.get("version_drift") or []),
    )


def _flatten_ingest(
    node: dict,
    out: dict[str, SourceVersion],
    via: tuple[str, ...],
) -> None:
    """Walk a single ingest's subtree, populating `out` with one entry per
    `infores:*` reached. The `via` chain captures intermediate-build ids
    between the ingest root and the current entry."""
    for child in node.get("sources") or []:
        cid = child.get("id")
        if not cid:
            continue
        # Every node with an id contributes a SourceVersion record. Even
        # intermediate builds (e.g. `infores:agr` with nested per-MOD
        # entries) are looked up by callers as the bundle-level fallback.
        out[cid] = SourceVersion(
            infores=cid,
            name=child.get("name") or "",
            version=child.get("version") or "",
            version_method=child.get("version_method") or "",
            retrieved_at=child.get("retrieved_at") or "",
            urls=tuple(child.get("urls") or ()),
            via=via,
        )
        # Recurse with this id appended to the via path so deeper entries
        # know they're nested below it.
        _flatten_ingest(child, out, via=(*via, cid))


def _pick_canonical_producer(
    by_producer: dict[str, dict[str, SourceVersion]],
) -> dict[str, str]:
    """For each infores, choose one producer ingest as canonical.

    Heuristic, in order of preference:
      1. An ingest whose id matches the infores' suffix (`infores:hgnc` →
         `hgnc-ingest`). Direct authoritative provider.
      2. Otherwise, an ingest whose subtree contains a `phenio` build
         (typically `kg-phenio`). All ontology terms in the merged KG come
         through phenio.
      3. Otherwise, first-seen producer.
    """
    all_infores: set[str] = set()
    for fmap in by_producer.values():
        all_infores.update(fmap.keys())

    canonical: dict[str, str] = {}
    for infores in all_infores:
        suffix = infores.split(":", 1)[-1] if ":" in infores else infores
        producers_with = [p for p, m in by_producer.items() if infores in m]

        # 1. Self-named ingest match (hgnc → hgnc-ingest).
        self_named = next(
            (p for p in producers_with if p == suffix or p == f"{suffix}-ingest"),
            None,
        )
        if self_named:
            canonical[infores] = self_named
            continue

        # 2. phenio-bearing producer for ontology-style infores.
        phenio_bearer = next(
            (p for p in producers_with if "phenio" in by_producer[p]),
            None,
        )
        if phenio_bearer:
            canonical[infores] = phenio_bearer
            continue

        # 3. Fallback.
        canonical[infores] = producers_with[0]

    return canonical


def resolve_for_edge(
    receipt: ResolvedReceipt,
    primary_knowledge_source: str | None,
    aggregator_knowledge_sources: Iterable[str] | None,
) -> SourceVersion | None:
    """Edge-level version lookup.

    Walks `aggregator_knowledge_sources`, drops `infores:monarchinitiative`,
    and uses the first remaining aggregator to identify the producing ingest.
    Inside that ingest's subtree, looks up the primary infores; falls back to
    the aggregator's own bundle-level entry if the primary isn't nested.

    When no non-monarch aggregator is present (direct ingest), looks the
    primary up across all producers and uses the canonical match.
    """
    aggregators = [
        a
        for a in (aggregator_knowledge_sources or ())
        if a and a != MONARCH_AGGREGATOR_INFORES
    ]

    if aggregators:
        # Walk aggregators in declaration order; first one whose producer we
        # can identify wins. (Most edges have exactly one non-monarch agg.)
        for agg in aggregators:
            producer = _producer_with_infores(receipt, agg)
            if producer is None:
                continue
            inner = receipt.by_producer.get(producer, {})
            # Prefer the per-component version when nested.
            if primary_knowledge_source and primary_knowledge_source in inner:
                return inner[primary_knowledge_source]
            # Fall back to the bundle-level aggregator entry.
            return inner.get(agg)
        return None

    # No non-monarch aggregator: edge came from a direct ingest. Look the
    # primary up under its canonical producer.
    if not primary_knowledge_source:
        return None
    canonical = receipt.canonical_producer.get(primary_knowledge_source)
    if canonical is None:
        return None
    return receipt.by_producer.get(canonical, {}).get(primary_knowledge_source)


def resolve_for_infores(
    receipt: ResolvedReceipt,
    infores: str,
) -> SourceVersion | None:
    """Node-level version lookup. Uses the canonical-producer heuristic."""
    canonical = receipt.canonical_producer.get(infores)
    if canonical is None:
        return None
    return receipt.by_producer.get(canonical, {}).get(infores)


def _producer_with_infores(
    receipt: ResolvedReceipt,
    infores: str,
) -> str | None:
    """Find the producer-ingest id that has this infores in its subtree.
    First match wins; ambiguity is rare in practice (one ingest per agg)."""
    for producer, fmap in receipt.by_producer.items():
        if infores in fmap:
            return producer
    return None
