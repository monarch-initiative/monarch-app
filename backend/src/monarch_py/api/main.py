import logging

import google
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.logger import logger
from monarch_py.api import association, entity, histopheno, search, semsim
from monarch_py.api.config import oak
from monarch_py.api.middleware.gcloud_logging import CloudLoggingMiddleware
from monarch_py.api.middleware.gcloud_logging import CloudLogFilter
from monarch_py.api.middleware.logging_middleware import LoggingMiddleware
from monarch_py.service.curie_service import CurieService
from google.cloud.logging_v2.resource import Resource

PREFIX = "/v3/api"

app = FastAPI(
    docs_url="/v3/docs",
    redoc_url="/v3/redoc",
)


def setup_cloud_logging():
    client = google.cloud.logging_v2.Client()
    client.setup_logging()

    handler = client.get_default_handler()
    handler.resource = Resource(type="api", labels={"service": "monarch-api"})
    handler.setLevel(logging.DEBUG)
    handler.filters = []
    # handler.addFilter(CloudLogFilter(project=client.project))
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.info("Logging initialized")


@app.on_event("startup")
async def initialize_app():
    oak()
    # Let the curie service singleton initialize itself
    CurieService()
    # todo: if production
    setup_cloud_logging()


app.include_router(entity.router, prefix=f"{PREFIX}/entity")
app.include_router(association.router, prefix=f"{PREFIX}/association")
app.include_router(search.router, prefix=PREFIX)
app.include_router(histopheno.router, prefix=f"{PREFIX}/histopheno")
app.include_router(semsim.router, prefix=f"{PREFIX}/semsim")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(CloudLoggingMiddleware)


@app.get("/")
async def _root():
    return RedirectResponse(url="/v3/docs")


@app.get("/api")
async def _api():
    return RedirectResponse(url="/v3/docs")


def run():
    uvicorn.run("monarch_py.api.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run()
