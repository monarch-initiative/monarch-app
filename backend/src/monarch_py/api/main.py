from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from monarch_py.api import (
    association,
    case_phenotype,
    entity,
    entity_grid,
    histopheno,
    meta,
    pathograph,
    search,
    semsim,
    sources_versions,
    text_annotation,
)
from monarch_py.api.config import semsimian, spacyner, settings
from monarch_py.api.middleware.logging_middleware import LoggingMiddleware
from monarch_py.service.solr_service import SolrQueryError
from monarch_py.utils.utils import get_release_metadata, get_release_versions, set_log_level

# At import, so startup logging is covered too and not just request handling. The CLI
# sets its own level; without this the API keeps loguru's default DEBUG sink.
set_log_level(settings.log_level)

PREFIX = "/v3/api"

app = FastAPI(
    docs_url="/v3/docs",
    redoc_url="/v3/redoc",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    semsimian()
    spacyner()
    # oak()
    yield


app.include_router(association.router, prefix=f"{PREFIX}/association")
app.include_router(case_phenotype.router, prefix=f"{PREFIX}/case-phenotype-matrix")
app.include_router(entity.router, prefix=f"{PREFIX}/entity")
app.include_router(entity_grid.router, prefix=f"{PREFIX}/entity")
app.include_router(histopheno.router, prefix=f"{PREFIX}/histopheno")
app.include_router(meta.router, prefix=PREFIX)
app.include_router(pathograph.router, prefix=f"{PREFIX}/pathograph")
app.include_router(search.router, prefix=PREFIX)
app.include_router(semsim.router, prefix=f"{PREFIX}/semsim")
app.include_router(sources_versions.router, prefix=PREFIX)
app.include_router(text_annotation.router, prefix=PREFIX)

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)


@app.exception_handler(SolrQueryError)
async def solr_query_error_handler(request: Request, exc: SolrQueryError) -> JSONResponse:
    """Report a query Solr refused as a bad request rather than a server error.

    A 500 says the server broke, which sends the reader looking at the server. These
    come from the query, which is often something the caller can act on -- too many
    IDs, bad filter syntax -- and when it isn't, the status still points at the right
    place. A Solr that is down or overloaded does not come through here and stays a 500.
    """
    return JSONResponse(status_code=400, content={"detail": f"Solr rejected the query: {exc.message}"})


app.description = """

# This is the v3 Monarch API.

This API is a RESTful web service that provides programmatic access to the Monarch Initiative's knowledge graph,
and which serves as the backend to the [Monarch Initiative's website](https://monarchinitiative.org).
"""


@app.get("/")
async def _root():
    return RedirectResponse(url="/v3/docs")


@app.get("/api")
async def _api():
    return RedirectResponse(url="/v3/docs")


@app.get(f"{PREFIX}/releases")
async def _v3(
    dev: bool = Query(default=False, title="Get dev releases of the KG (default False)"),
    limit: int = Query(default=0, title="The number of releases to return (default 0 for no limit)"),
    release: str = Query(default=None, title="Get metadata for a specific release"),
):
    if release is None:
        return get_release_versions(dev=dev, limit=limit)
    return get_release_metadata(release=release, dev=dev)


@app.get(f"{PREFIX}/version")
async def _version():
    return {
        "monarch_kg_version": settings.monarch_kg_version,
        "monarch_api_version": settings.monarch_api_version,
        "monarch_kg_source": settings.monarch_kg_source,
    }


def run():
    uvicorn.run("monarch_py.api.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run()
