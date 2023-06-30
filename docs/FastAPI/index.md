# Monarch-Py FastAPI

An optional FastAPI is also available for browsing the knowledge graph produced by the Monarch Initiative, which wraps the `monarch-py` library.

It can be installed as an extra of `monarch-py` via pip or pipx:
```bash
pip|pipx install monarch-py[api]
```

## Running the API

A local development server can be started using `uvicorn` via the included Makefile:
```bash
cd <path-to>/monarch-app
make dev-api
```

The API is then available at `http://127.0.0.1:8000/v3/api`.

Swagger documentation is available at `http://127.0.0.1:8000/v3/docs`,  
and a ReDoc interface at `http://127.0.0.1:8000/v3/redoc`.

##  Documentation

[API Reference](./Endpoints/index.md)

[Data Response Model](../Data-Model/index.md)

