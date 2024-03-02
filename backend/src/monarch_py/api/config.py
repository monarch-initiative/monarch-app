import os
from functools import lru_cache

from pydantic import BaseModel

from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.implementations.spacy.spacy_implementation import SpacyImplementation
from monarch_py.service.semsim_service import SemsimianService


class Settings(BaseModel):
    solr_host: str = os.getenv("SOLR_HOST") if os.getenv("SOLR_HOST") else "127.0.0.1"
    solr_port: str = os.getenv("SOLR_PORT") if os.getenv("SOLR_PORT") else 8983
    solr_url: str = os.getenv("SOLR_URL") if os.getenv("SOLR_URL") else f"http://{solr_host}:{solr_port}/solr"
    phenio_db_path: str = os.getenv("PHENIO_DB_PATH") if os.getenv("PHENIO_DB_PATH") else "/data/phenio.db"

    semsim_server_host: str = os.getenv("SEMSIM_SERVER_HOST", "127.0.0.1")
    semsim_server_port: str = os.getenv("SEMSIM_SERVER_PORT", 9999)


settings = Settings()


@lru_cache(maxsize=1)
def solr():
    return SolrImplementation(settings.solr_url)


@lru_cache(maxsize=1)
def semsimian():
    return SemsimianService(
        semsim_server_host=settings.semsim_server_host,
        semsim_server_port=settings.semsim_server_port,
        entity_implementation=solr(),
    )


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
