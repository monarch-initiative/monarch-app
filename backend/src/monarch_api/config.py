import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    solr_url = (
        os.getenv("SOLR_URL") if os.getenv("SOLR_URL") else "http://127.0.0.1:8983/solr"
    )


settings = Settings()
