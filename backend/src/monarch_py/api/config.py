import os
from functools import lru_cache

from pydantic import BaseModel

from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.implementations.spacy.spacy_implementation import SpacyImplementation
from monarch_py.service.semsim_service import SemsimianService


def _int_env(name: str, default: int) -> int:
    """Parse an int env var, falling back to `default` on missing/non-integer values.
    Avoids crashing the whole API worker at import time if e.g. DUCKSIM_THREADS is set
    to a non-integer."""
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


class Settings(BaseModel):
    solr_host: str = os.getenv("SOLR_HOST") if os.getenv("SOLR_HOST") else "127.0.0.1"
    solr_port: str = os.getenv("SOLR_PORT") if os.getenv("SOLR_PORT") else 8983
    solr_url: str = os.getenv("SOLR_URL") if os.getenv("SOLR_URL") else f"http://{solr_host}:{solr_port}/solr"
    phenio_db_path: str = os.getenv("PHENIO_DB_PATH") if os.getenv("PHENIO_DB_PATH") else "/data/phenio.db"

    semsim_server_host: str = os.getenv("SEMSIM_SERVER_HOST", "127.0.0.1")
    semsim_server_port: str = os.getenv("SEMSIM_SERVER_PORT", 9999)

    # similarity backend: "semsimian" (legacy HTTP semsimian-server, default) or "ducksim"
    # (in-process DuckDB over monarch-kg.duckdb). Opt in with SEMSIM_BACKEND=ducksim, or per-request
    # via the hidden ?engine=ducksim API param.
    monarch_kg_duckdb_path: str = os.getenv("MONARCH_KG_DUCKDB_PATH", "/data/monarch-kg.duckdb")
    semsim_backend: str = os.getenv("SEMSIM_BACKEND", "semsimian")
    # per-worker DuckDB caps (tunable for memory-constrained hosts: workers x limit must fit RAM)
    ducksim_memory_limit: str = os.getenv("DUCKSIM_MEMORY_LIMIT", "2GB")
    ducksim_threads: int = _int_env("DUCKSIM_THREADS", 2)

    monarch_kg_version: str = os.getenv("MONARCH_KG_VERSION", "unknown")
    monarch_api_version: str = os.getenv("MONARCH_API_VERSION", "unknown")
    monarch_kg_source: str = os.getenv("MONARCH_KG_SOURCE", "unknown")

    # Read the build receipt from `data.m.o/monarch-kg-dev/` instead of
    # `monarch-kg/` when the env var is truthy. Useful while the new-shape
    # metadata.yaml has only landed on dev. Run as e.g.:
    #   MONARCH_KG_USE_DEV=1 make dev-api
    monarch_kg_use_dev: bool = os.getenv("MONARCH_KG_USE_DEV", "").lower() in (
        "1",
        "true",
        "yes",
    )


settings = Settings()


@lru_cache(maxsize=1)
def solr():
    return SolrImplementation(settings.solr_url)


@lru_cache(maxsize=1)
def ducksim():
    """In-process DuckDB similarity engine over the read-only monarch-kg.duckdb artifact."""
    from monarch_py.service.ducksim import Ducksim
    from monarch_py.service.ducksim_service import DucksimService

    engine = Ducksim.from_duckdb(
        settings.monarch_kg_duckdb_path,
        memory_limit=settings.ducksim_memory_limit,
        threads=settings.ducksim_threads,
    )
    return DucksimService(engine=engine, entity_implementation=solr())


@lru_cache(maxsize=1)
def semsimian_http():
    """Legacy similarity backend: HTTP calls to semsimian-server."""
    return SemsimianService(
        semsim_server_host=settings.semsim_server_host,
        semsim_server_port=settings.semsim_server_port,
        entity_implementation=solr(),
    )


def semsim_service(engine: str = None):
    """Resolve the similarity backend. A per-request `engine` ("ducksim" | "semsimian") overrides
    the SEMSIM_BACKEND default — exposed via a hidden ?engine= API param for A/B comparison."""
    chosen = (engine or settings.semsim_backend or "semsimian").lower()
    return ducksim() if chosen == "ducksim" else semsimian_http()


def semsimian():
    """Default-backend resolver kept for existing callers (CLI, etc.)."""
    return semsim_service()


@lru_cache(maxsize=1)
def oak():
    return NotImplementedError("OAK is temporarily disabled")


#    oak_implementation = OakImplementation()
#    oak_implementation.init_phenio_adapter(force_update=False, phenio_path=settings.phenio_db_path)
#    return oak_implementation


@lru_cache(maxsize=1)
def spacyner():
    spacy_implementation = SpacyImplementation()
    spacy_implementation.init_spacy(grounding_implementation=solr())
    return spacy_implementation
