from fastapi import FastAPI, Depends
import requests

from monarch_api.utils import *
from monarch_api import entity, association

app = FastAPI()
app.include_router(entity.router)
app.include_router(association.router)

base_url = 'http://localhost:8983/solr'


@app.get("/solr")
async def test():
    """For dev purposes. can get rid of later"""
    r = requests.get(base_url)
    return {"SOLR Connection status": f"{r.status_code}"}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api")
async def api():
    return f"For API documentation, see {base_url}/docs"
