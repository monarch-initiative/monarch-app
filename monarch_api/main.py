from fastapi import FastAPI

#import requests as r
import pysolr

app = FastAPI()

solr = pysolr.Solr(
    'http://localhost:8983/solr/', 
    #always_commit=True, 
    #[timeout=10], 
    #[auth=<type of authentication>]
)
solr.ping()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api")
async def api():
    return {"data": "This wil eventually be the API home page"}