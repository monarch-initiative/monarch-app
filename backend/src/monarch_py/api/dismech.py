"""Experimental dismech integrations, served from dismech.duckdb (see scripts/dismech_db.py).

Unadvertised (not in the OpenAPI schema) while the response shapes are still changing. Every
endpoint 404s when DISMECH_DUCKDB_PATH isn't configured.
"""

import re
from typing import Literal

from fastapi import APIRouter, HTTPException, Path, Query

from monarch_py.api.config import dismech_store

router = APIRouter(tags=["dismech"], responses={404: {"description": "Not Found"}})

_MONDO = re.compile(r"^MONDO:\d{7}$")
_PHENOTYPE = re.compile(r"^(HP|UPHENO):\d{7}$")
_GENE_OR_DISEASE = re.compile(r"^(HGNC:\d+|MONDO:\d{7})$")
_TREATMENT_ID = re.compile(r"^(MONDO:\d{7}|(CHEBI|NCIT|RXCUI|DRUGBANK|UNII|MESH):[A-Z0-9]+)$")
_TERM = re.compile(r"^(GO|CL|UBERON):\d+$")


def _store(id: str, pattern: re.Pattern, expected: str):
    if not pattern.match(id):
        raise HTTPException(status_code=400, detail=f"Expected {expected}")
    store = dismech_store()
    if store is None:
        raise HTTPException(status_code=404, detail="dismech integrations are not configured")
    return store


def _page(corroborated_only: bool, dismech_only: bool, limit: int | None, offset: int) -> dict:
    return {"corroborated_only": corroborated_only, "dismech_only": dismech_only, "limit": limit, "offset": offset}


@router.get("/status", include_in_schema=False)
def _status() -> dict:
    """Whether dismech integrations are served, and from which dismech release"""
    store = dismech_store()
    if store is None:
        raise HTTPException(status_code=404, detail="dismech integrations are not configured")
    return {"release": store.release}


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
    """Diseases with a phenotype or a subclass of it, collapsed across primary knowledge sources, with dismech corroboration"""
    store = _store(id, _PHENOTYPE, "an HP or UPHENO id")
    return store.phenotype_diseases(id, **_page(corroborated_only, dismech_only, limit, offset))


@router.get("/gene-disease-profile/{id}", include_in_schema=False)
def _gene_disease_profile(
    id: str = Path(examples=["HGNC:870", "MONDO:0010200"]),
    kind: Literal["causal", "correlated"] = Query("causal", description="KG association category"),
    corroborated_only: bool = Query(False, description="Only rows dismech corroborates"),
    dismech_only: bool = Query(False, description="Include pairs only dismech records"),
    limit: int | None = Query(10, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict:
    """A gene's diseases or a disease's genes collapsed across sources, with dismech's genetics records"""
    store = _store(id, _GENE_OR_DISEASE, "an HGNC or MONDO id")
    return store.gene_disease_profile(id, kind, **_page(corroborated_only, dismech_only, limit, offset))


@router.get("/treatments/{id}", include_in_schema=False)
def _treatments(
    id: str = Path(examples=["MONDO:0010200", "CHEBI:39867"]),
    name: str | None = Query(None, max_length=200, description="Drug name, matched as a whole word"),
) -> dict:
    """dismech treatments for a disease, or the diseases a drug is used for, with mechanism targets"""
    store = _store(id, _TREATMENT_ID, "a MONDO id or a drug CURIE")
    return store.treatments(id, name=None if id.startswith("MONDO:") else name)


@router.get("/term-diseases/{id}", include_in_schema=False)
def _term_diseases(
    id: str = Path(examples=["CL:0000182", "GO:0006825"]),
    limit: int | None = Query(10, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict:
    """Diseases whose dismech mechanisms involve a GO process, CL cell type or UBERON location"""
    store = _store(id, _TERM, "a GO, CL or UBERON id")
    return store.term_diseases(id, limit=limit, offset=offset)
