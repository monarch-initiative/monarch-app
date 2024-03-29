import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from monarch_py.api import association, entity, histopheno, search, semsim, text_annotation
from monarch_py.api.config import semsimian, spacyner
from monarch_py.api.middleware.logging_middleware import LoggingMiddleware

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

# This is the v3 Monarch API, the Biolink API is still available through March 20th, 2023 

The Biolink API (Monarch v1/v2) is available at 
[http://api-biolink.monarchinitiative.org](http://api-biolink.monarchinitiative.org), 
but will be [shut down on March 20th, 2023](http://monarchinit.medium.com/migrating-to-the-new-monarch-infrastructure-fe9d98ccf64a).
"""


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
