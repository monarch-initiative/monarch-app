# Monarch-Py FastAPI

A FastAPI is also available for browsing the knowledge graph produced by the Monarch Initiative, which wraps the `monarch-py` library.

It is included automatically as part of `monarch-py` when installed via pip or pipx.

## Running the API Server

A local development server can be started with the command:

```bash
monarch-api
```

or using `uvicorn`:

```bash
# Using uvicorn directly:
poetry run uvicorn src.monarch_py.api.main:app --reload

# Using the Makefile shortcut:
cd <path-to>/monarch-app
make dev-api
```

The API is then available at `http://127.0.0.1:8000/v3/api`.

Swagger documentation is available at `http://127.0.0.1:8000/v3/docs`,  
and a ReDoc interface at `http://127.0.0.1:8000/v3/redoc`.

## Documentation

[API Reference](./Endpoints/index.md)

[Data Response Model](../Data-Model/index.md)
