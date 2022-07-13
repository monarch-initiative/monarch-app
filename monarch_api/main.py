from fastapi import FastAPI, Depends
import requests

from monarch_api.utils import *
from monarch_api import entity, association

app = FastAPI()
app.include_router(entity.router)
app.include_router(association.router)

base_url = 'http://localhost:8983/solr'


@app.get("/")
async def root():
    return f"Monarch API - for API documentation, see {base_url}/docs"

@app.get("/api")
async def api():
    return f"Monarch API - for API documentation, see {base_url}/docs"
