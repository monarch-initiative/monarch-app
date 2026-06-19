"""API endpoint serving dismech pathographs for disease and gene pages.

Proxies the dismech pathograph artifact (``index.json``, ``by_gene.json`` and
per-disorder ``MONDO_<id>.json`` files) so the frontend fetches same-origin —
no CORS — and so the gene-page anchor-merge happens once, server-side, instead
of N cross-origin fetches in the browser.

The artifact base is ``settings.dismech_pathographs_url`` (a published URL in
prod, a local directory while developing against an un-pushed dismech export).
"""

from __future__ import annotations

import json
import re
import threading
import time
from pathlib import Path
from typing import Any

import requests
from fastapi import APIRouter, HTTPException, Path as PathParam

from monarch_py.api.additional_models import (
    Pathograph,
    PathographEdge,
    PathographNode,
    PathographSource,
)
from monarch_py.api.config import settings

router = APIRouter(tags=["pathograph"], responses={404: {"description": "Not Found"}})

# CURIE shape — node ids feed artifact lookups, so keep them strict.
_CURIE_PATTERN = re.compile(r"^[A-Za-z]+:[A-Za-z0-9]+$")

# index.json / by_gene.json are hit on every request; cache them briefly.
_INDEX_TTL_SECONDS = 300
_index_cache: dict[str, tuple[float, dict]] = {}
_index_lock = threading.Lock()


def _read_artifact(name: str) -> str | None:
    """Read one artifact file by name from the configured base (URL or dir)."""
    base = settings.dismech_pathographs_url
    if base.startswith(("http://", "https://")):
        try:
            resp = requests.get(f"{base.rstrip('/')}/{name}", timeout=15)
        except requests.RequestException as e:
            raise HTTPException(status_code=502, detail=f"Failed to fetch {name}: {e}") from e
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.text
    path = Path(base) / name
    return path.read_text() if path.exists() else None


def _load_index(name: str) -> dict:
    """Load and cache a top-level index artifact (index.json or by_gene.json)."""
    with _index_lock:
        cached = _index_cache.get(name)
        if cached and (time.time() - cached[0]) < _INDEX_TTL_SECONDS:
            return cached[1]
    text = _read_artifact(name)
    if text is None:
        raise HTTPException(status_code=502, detail=f"Pathograph artifact {name} is unavailable")
    data = json.loads(text)
    with _index_lock:
        _index_cache[name] = (time.time(), data)
    return data


def _anchor_id(node: dict[str, Any]) -> str | None:
    """Stable cross-disorder id for nodes that should be boxed when merging.

    Phenotypes box on their HP term id; single-gene genetic nodes box on the
    HGNC id. Everything else (free-text mechanism nodes) stays disorder-local.
    """
    meta = node.get("meta") or {}
    if node.get("node_type") == "phenotype" and meta.get("term_id"):
        return f"HP:{str(meta['term_id']).split(':')[-1]}"
    gene_ids = [gt["id"] for gt in (meta.get("gene_terms") or []) if gt.get("id")]
    if node.get("node_type") == "genetic" and len(gene_ids) == 1:
        return f"GENE:{gene_ids[0].lower()}"
    return None


def _disorder_url(slug: str | None) -> str | None:
    """Deep link to a disorder's dismech page, from the slug carried in index.json."""
    if not slug:
        return None
    return f"{settings.dismech_site_url.rstrip('/')}/pages/disorders/{slug}.html"


def _merge(graphs: list[tuple[str, str, str | None, dict]]) -> tuple[list[PathographNode], list[PathographEdge]]:
    """Anchor-merge per-disorder graphs into one.

    Shared phenotypes/genes collapse to a single boxed node (carrying every
    contributing Mondo id in ``sources``); disorder-local mechanism nodes are
    namespaced by Mondo id so they never collide. For a single graph this is a
    faithful pass-through.
    """
    nodes: dict[str, PathographNode] = {}
    edges: dict[tuple[str, str, str | None], PathographEdge] = {}

    for mondo, _name, _slug, graph in graphs:
        local_to_gid: dict[str, str] = {}
        for node in graph.get("nodes", []):
            gid = _anchor_id(node) or f"{mondo}::{node['id']}"
            local_to_gid[node["id"]] = gid
            existing = nodes.get(gid)
            if existing is None:
                nodes[gid] = PathographNode(
                    id=gid,
                    label=node["id"],
                    node_type=node.get("node_type", "unknown"),
                    color=node.get("color"),
                    is_orphan=node.get("is_orphan", False),
                    description=node.get("description"),
                    meta=node.get("meta"),
                    sources=[mondo],
                )
            else:
                if mondo not in existing.sources:
                    existing.sources.append(mondo)
                # A node defined for real in any disorder beats an orphan stub.
                if existing.is_orphan and not node.get("is_orphan", False):
                    existing.is_orphan = False
                    existing.node_type = node.get("node_type", existing.node_type)
                    existing.color = node.get("color", existing.color)
                    existing.label = node["id"]
                existing.description = existing.description or node.get("description")
                existing.meta = existing.meta or node.get("meta")

        for edge in graph.get("edges", []):
            source = local_to_gid.get(edge["source"])
            target = local_to_gid.get(edge["target"])
            if source is None or target is None:
                continue
            key = (source, target, edge.get("predicate"))
            existing_edge = edges.get(key)
            if existing_edge is None:
                edges[key] = PathographEdge(
                    source=source,
                    target=target,
                    predicate=edge.get("predicate"),
                    description=edge.get("description"),
                    sources=[mondo],
                )
            elif mondo not in existing_edge.sources:
                existing_edge.sources.append(mondo)

    return list(nodes.values()), list(edges.values())


def _collect_graphs(mondo_ids: list[str], index: dict) -> list[tuple[str, str, str | None, dict]]:
    """Load every disorder graph for the given Mondo ids (with name + dismech slug)."""
    collected: list[tuple[str, str, str | None, dict]] = []
    for mondo in mondo_ids:
        for entry in index.get(mondo, []):
            text = _read_artifact(entry["file"])
            if text is None:
                continue
            collected.append((mondo, entry.get("name", mondo), entry.get("slug"), json.loads(text)))
    return collected


@router.get("/{node_id}")
def _get_pathograph(
    node_id: str = PathParam(
        title="Disease (MONDO) or gene (HGNC) id to fetch a pathograph for",
        examples=["MONDO:0018923", "HGNC:870"],
    ),
) -> Pathograph:
    """Return a dismech pathograph for a disease or gene node.

    Disease (``MONDO:…``) returns that disorder's pathograph. Gene (``HGNC:…``)
    returns every disorder pathograph the gene participates in, anchor-merged
    into one graph. 404 when no pathograph exists for the node.
    """
    if not _CURIE_PATTERN.match(node_id):
        raise HTTPException(status_code=400, detail="Invalid node id; expected a CURIE like MONDO:0018923")

    upper = node_id.upper()
    index = _load_index("index.json")

    if upper.startswith("MONDO:"):
        if upper not in index:
            raise HTTPException(status_code=404, detail=f"No pathograph for {upper}")
        mondo_ids = [upper]
        category = "disease"
    elif upper.startswith("HGNC:"):
        by_gene = _load_index("by_gene.json")
        mondo_ids = by_gene.get(node_id.lower())
        if not mondo_ids:
            raise HTTPException(status_code=404, detail=f"No pathographs reference {upper}")
        category = "gene"
    else:
        raise HTTPException(
            status_code=404, detail=f"Pathographs are only available for diseases and genes, not {upper}"
        )

    graphs = _collect_graphs(mondo_ids, index)
    if not graphs:
        raise HTTPException(status_code=404, detail=f"No pathograph data found for {upper}")

    nodes, edges = _merge(graphs)
    # De-dupe contributing disorders, preserving first-seen order.
    sources: dict[str, tuple[str, str | None]] = {}
    for mondo, name, slug, _graph in graphs:
        sources.setdefault(mondo, (name, slug))

    return Pathograph(
        node_id=upper,
        category=category,
        nodes=nodes,
        edges=edges,
        sources=[
            PathographSource(id=mondo, name=name, url=_disorder_url(slug))
            for mondo, (name, slug) in sources.items()
        ],
    )
