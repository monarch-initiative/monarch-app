"""API endpoint exposing per-source version info from the build receipt."""

from __future__ import annotations

import time
from dataclasses import asdict

import requests
import yaml
from fastapi import APIRouter, HTTPException

from monarch_py.utils.source_versions import (
    ResolvedReceipt,
    index_receipt,
)
from monarch_py.utils.utils import KG_DEV_URL, KG_URL

router = APIRouter(tags=["sources"])

# 5-minute TTL on the parsed receipt — release cadence is daily-ish, but we
# don't want a five-second window between two requests to refetch.
_CACHE_TTL_SECONDS = 300

_cache: dict[tuple[str, bool], tuple[float, ResolvedReceipt]] = {}


def _try_url(url: str) -> dict | None:
    """GET the receipt; return parsed YAML on success, None on missing/legacy."""
    try:
        resp = requests.get(url, timeout=15)
    except requests.RequestException:
        return None
    if resp.status_code != 200:
        return None
    try:
        receipt = yaml.safe_load(resp.text)
    except yaml.YAMLError:
        return None
    # The pre-collapse legacy `metadata.yaml` (kg-version + packages + data)
    # has no top-level `id` — treat as missing so the caller can fall back.
    if not isinstance(receipt, dict) or "id" not in receipt:
        return None
    return receipt


def _fetch_receipt(release: str = "latest", dev: bool = False) -> ResolvedReceipt:
    """Fetch + parse + index `metadata.yaml` for the given release.

    If `dev` is False (the default), tries the production
    (`data.m.o/monarch-kg/...`) URL first, then transparently falls back
    to the dev mirror — useful while the new-shape receipt has only
    landed on dev. `dev=True` skips prod entirely.

    Cached for `_CACHE_TTL_SECONDS` per (release, dev) pair.
    """
    key = (release, dev)
    cached = _cache.get(key)
    if cached and (time.time() - cached[0]) < _CACHE_TTL_SECONDS:
        return cached[1]

    candidates = (
        [f"{KG_DEV_URL}/{release}/metadata.yaml"]
        if dev
        else [
            f"{KG_URL}/{release}/metadata.yaml",
            f"{KG_DEV_URL}/{release}/metadata.yaml",
        ]
    )

    receipt: dict | None = None
    last_url = ""
    for url in candidates:
        last_url = url
        receipt = _try_url(url)
        if receipt is not None:
            break

    if receipt is None:
        raise HTTPException(
            status_code=502,
            detail=(
                f"No new-shape build receipt found at any of: {', '.join(candidates)} "
                "(production receipt may still be the pre-collapse format)."
            ),
        )

    resolved = index_receipt(receipt)
    _cache[key] = (time.time(), resolved)
    return resolved


def _serialize(receipt: ResolvedReceipt) -> dict:
    return {
        "release": receipt.release,
        "generated_at": receipt.generated_at,
        "by_producer": {
            producer: {infores: asdict(sv) for infores, sv in entries.items()}
            for producer, entries in receipt.by_producer.items()
        },
        "canonical_producer": receipt.canonical_producer,
        "disagreements": receipt.disagreements,
        "version_drift": receipt.version_drift,
    }


@router.get("/sources/versions")
def sources_versions(release: str = "latest", dev: bool = False) -> dict:
    """Return the resolved version index for a given monarch-kg release.

    Default is `latest`, which resolves to the most recent published release
    on `data.monarchinitiative.org`. Specific dates (`2026-05-07`) are also
    accepted for retrospective lookups. Pass `dev=true` to bypass the
    production URL entirely and only consult `monarch-kg-dev/`.
    """
    return _serialize(_fetch_receipt(release, dev=dev))
