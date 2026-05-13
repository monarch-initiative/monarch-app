"""API endpoint exposing per-source version info from the build receipt."""

from __future__ import annotations

import re
import threading
import time
from dataclasses import asdict

import requests
import yaml
from fastapi import APIRouter, HTTPException

from monarch_py.api.config import settings
from monarch_py.utils.source_versions import (
    ResolvedReceipt,
    index_receipt,
)
from monarch_py.utils.utils import KG_DEV_URL, KG_URL

router = APIRouter(tags=["sources"])

# 5-minute TTL on the parsed receipt — release cadence is daily-ish, but we
# don't want a five-second window between two requests to refetch.
_CACHE_TTL_SECONDS = 300

# Release identifiers we accept: `latest`, dated builds (`2026-05-07`), and
# tagged builds (`v2026-05-07`). Strict enough that the value can't break out
# of the URL path or include unexpected characters.
_RELEASE_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")

_cache: dict[tuple[str, bool], tuple[float, ResolvedReceipt]] = {}
_cache_lock = threading.Lock()


def _fetch_receipt(release: str = "latest", dev: bool = False) -> ResolvedReceipt:
    """Fetch + parse + index `metadata.yaml` for the given release.

    `dev=False` (default) reads from the production
    `data.m.o/monarch-kg/...` mirror; `dev=True` reads from the
    `data.m.o/monarch-kg-dev/...` mirror — handy locally while the
    new-shape receipt is still only landing on dev. Cached for
    `_CACHE_TTL_SECONDS` per (release, dev) pair.

    Cache access is guarded by `_cache_lock`. Two concurrent requests for the
    same uncached key may both issue the upstream fetch (we don't hold the
    lock across I/O); whichever finishes second harmlessly overwrites the
    first. This is much rarer than the in-process race on plain dict access.
    """
    key = (release, dev)
    with _cache_lock:
        cached = _cache.get(key)
        if cached and (time.time() - cached[0]) < _CACHE_TTL_SECONDS:
            return cached[1]

    base = KG_DEV_URL if dev else KG_URL
    url = f"{base}/{release}/metadata.yaml"
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

    if not isinstance(receipt, dict) or "id" not in receipt:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Build receipt at {url} doesn't carry a top-level `id` "
                "(probably the pre-collapse legacy shape). Pass `?dev=true` "
                "to read from monarch-kg-dev/ in the meantime."
            ),
        )

    resolved = index_receipt(receipt)
    with _cache_lock:
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
    }


@router.get("/sources/versions")
def sources_versions(release: str | None = None, dev: bool | None = None) -> dict:
    """Return the resolved version index for a given monarch-kg release.

    Default is the release this API was built against (the `MONARCH_KG_VERSION`
    env var, surfaced in `/version`), so the receipt reflects the bytes
    actually in the deployed Solr/DuckDB. Falls back to `latest` when the env
    var is unset. Specific dates (`2026-05-07`) are also accepted for
    retrospective lookups. Pass `dev=true` to read from `monarch-kg-dev/`;
    otherwise the deployment-wide default applies (set via the
    `MONARCH_KG_USE_DEV` env var, default false).
    """
    resolved_release = release if release is not None else _default_release()
    if not _RELEASE_PATTERN.match(resolved_release):
        raise HTTPException(
            status_code=400,
            detail="Invalid release identifier; expected alphanumerics, `.`, `_`, or `-`.",
        )
    use_dev = settings.monarch_kg_use_dev if dev is None else dev
    return _serialize(_fetch_receipt(resolved_release, dev=use_dev))


def _default_release() -> str:
    """Pin the receipt URL to the deployed build when we know which one it is.

    `MONARCH_KG_VERSION` is set per-deploy by monarch-stack-v3 and seeds
    `settings.monarch_kg_version`. Unset → the Settings default `"unknown"`,
    which means we're running locally or the deploy didn't pass it through;
    fall back to `latest` so the endpoint still does something useful.
    """
    pinned = settings.monarch_kg_version
    if not pinned or pinned == "unknown":
        return "latest"
    return pinned
