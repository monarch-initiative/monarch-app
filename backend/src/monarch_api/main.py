import uvicorn
from fastapi import FastAPI

from monarch_api import association, entity, histopheno, search

app = FastAPI()
app.include_router(entity.router)
app.include_router(association.router)
app.include_router(search.router)
app.include_router(histopheno.router)


@app.get("/")
async def _root():
    return f"Monarch API - for API documentation, see /docs"


@app.get("/api")
async def _api():
    return f"Monarch API - for API documentation, see /docs"


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
