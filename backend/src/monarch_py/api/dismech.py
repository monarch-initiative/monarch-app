"""Experimental dismech integrations, served from dismech.duckdb (see scripts/dismech_db.py).

Unadvertised (not in the OpenAPI schema) while the response shapes are still changing. Every
endpoint 404s when DISMECH_DUCKDB_PATH isn't configured.
"""

import re

from fastapi import APIRouter, HTTPException, Path, Query

from monarch_py.api.config import dismech_store

router = APIRouter(tags=["dismech"], responses={404: {"description": "Not Found"}})

_MONDO = re.compile(r"^MONDO:\d{7}$")
_HP = re.compile(r"^HP:\d{7}$")
_DRUG = re.compile(r"^(CHEBI|NCIT):[A-Z]?\d+$")
_TERM = re.compile(r"^(GO|CL|UBERON|CHEBI|HGNC):\d+$")


def _store(id: str, pattern: re.Pattern, expected: str):
    if not pattern.match(id):
        raise HTTPException(status_code=400, detail=f"Expected {expected}")
    store = dismech_store()
    if store is None:
        raise HTTPException(status_code=404, detail="dismech integrations are not configured")
    return store


def _page(corroborated_only: bool, dismech_only: bool, limit: int | None, offset: int) -> dict:
    return {"corroborated_only": corroborated_only, "dismech_only": dismech_only, "limit": limit, "offset": offset}


@router.get("/phenotype-profile/{id}", include_in_schema=False)
def _phenotype_profile(
    id: str = Path(examples=["MONDO:0010200"]),
    corroborated_only: bool = Query(False, description="Only rows dismech corroborates"),
    dismech_only: bool = Query(False, description="Include phenotypes only dismech records"),
    limit: int | None = Query(None, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict:
    """A disease's phenotypes collapsed across primary knowledge sources, with dismech corroboration"""
    store = _store(id, _MONDO, "a MONDO id")
    return store.phenotype_profile(id, **_page(corroborated_only, dismech_only, limit, offset))


@router.get("/phenotype-diseases/{id}", include_in_schema=False)
def _phenotype_diseases(
    id: str = Path(examples=["HP:0001394"]),
    corroborated_only: bool = Query(False, description="Only rows dismech corroborates"),
    dismech_only: bool = Query(False, description="Include diseases only dismech records"),
    limit: int | None = Query(25, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict:
    """Diseases with a phenotype collapsed across primary knowledge sources, with dismech corroboration"""
    store = _store(id, _HP, "an HP id")
    return store.phenotype_diseases(id, **_page(corroborated_only, dismech_only, limit, offset))


@router.get("/treatments/{id}", include_in_schema=False)
def _treatments(id: str = Path(examples=["MONDO:0010200", "CHEBI:39867"])) -> dict:
    """dismech treatments for a disease, or the diseases a drug is used for, with mechanism targets"""
    store = _store(id, re.compile(f"{_MONDO.pattern}|{_DRUG.pattern}"), "a MONDO, CHEBI or NCIT id")
    return store.treatments(id)


@router.get("/mechanisms/{id}", include_in_schema=False)
def _mechanisms(id: str = Path(examples=["CL:0000182", "GO:0006825"])) -> dict:
    """dismech mechanisms annotated with an ontology term, and the phenotypes each leads to"""
    store = _store(id, _TERM, "a GO, CL, UBERON, CHEBI or HGNC id")
    return store.mechanisms(id)
