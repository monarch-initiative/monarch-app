import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from monarch_py.api import association, entity, histopheno, search, semsim
from monarch_py.api.config import oak

PREFIX = "/v3/api"

app = FastAPI(
    docs_url="/v3/docs",
    redoc_url="/v3/redoc",
)


@app.on_event("startup")
async def initialize_app():
    oak()


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
