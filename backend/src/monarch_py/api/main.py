import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from monarch_py.api import association, entity, histopheno, search, semsim, text_annotation
from monarch_py.api.config import semsimian, spacyner
from monarch_py.api.middleware.logging_middleware import LoggingMiddleware
from monarch_py.utils.utils import get_release_metadata, get_release_versions

PREFIX = "/v3/api"

app = FastAPI(
    docs_url="/v3/docs",
    redoc_url="/v3/redoc",
)


@app.on_event("startup")
async def initialize_app():
    semsimian()
    spacyner()
    # oak()


app.include_router(association.router, prefix=f"{PREFIX}/association")
app.include_router(entity.router, prefix=f"{PREFIX}/entity")
app.include_router(histopheno.router, prefix=f"{PREFIX}/histopheno")
app.include_router(search.router, prefix=PREFIX)
app.include_router(semsim.router, prefix=f"{PREFIX}/semsim")
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


def run():
    uvicorn.run("monarch_py.api.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run()
