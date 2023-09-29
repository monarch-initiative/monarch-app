#!/usr/bin/bash 

# check for uvicorn workers env var, default to 1
UVICORN_WORKERS=${UVICORN_WORKERS:-1}

# Start the API
/opt/poetry/bin/poetry run uvicorn src.monarch_py.api.main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS}
