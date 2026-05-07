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
from monarch_py.utils.utils import KG_URL

router = APIRouter(tags=["sources"])

# 5-minute TTL on the parsed receipt — release cadence is daily-ish, but we
# don't want a five-second window between two requests to refetch.
_CACHE_TTL_SECONDS = 300

_cache: dict[str, tuple[float, ResolvedReceipt]] = {}


def _fetch_receipt(release: str = "latest") -> ResolvedReceipt:
    """Fetch + parse + index `metadata.yaml` for the given release. Cached."""
    cached = _cache.get(release)
    if cached and (time.time() - cached[0]) < _CACHE_TTL_SECONDS:
        return cached[1]

    url = f"{KG_URL}/{release}/metadata.yaml"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch build receipt from {url}: {e}",
        ) from e

    try:
        receipt = yaml.safe_load(resp.text)
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Build receipt at {url} is not valid YAML: {e}",
        ) from e

    resolved = index_receipt(receipt or {})
    _cache[release] = (time.time(), resolved)
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
def sources_versions(release: str = "latest") -> dict:
    """Return the resolved version index for a given monarch-kg release.

    Default is `latest`, which resolves to the most recent published release
    on `data.monarchinitiative.org`. Specific dates (`2026-05-07`) are also
    accepted for retrospective lookups.
    """
    return _serialize(_fetch_receipt(release))
