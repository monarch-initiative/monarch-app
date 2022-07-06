from fastapi import FastAPI
#from monarch_api import entity
import requests

app = FastAPI()

solr = 'http://localhost:8983/solr'


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api")
async def api():
    return {"data": "This wil eventually be the API home page"}

# For dev purposes. can get rid of later
@app.get("/solr")
async def test():
    r = requests.get(solr)
    return {"SOLR Connection status": f"{r.status_code}"}

@app.get("/api/entity/{id}")
async def test(id):
    url = f"{solr}/entity/get?id={id}"
    r = requests.get(url)
    return {"Entity": f"{r.json()['doc']}"}
