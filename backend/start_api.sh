#!/usr/bin/bash 

# check for uvicorn workers env var, default to 8
UVICORN_WORKERS=${UVICORN_WORKERS:-8}

# Start the API
poetry run gunicorn src.monarch_py.api.main:app \
    --bind 0.0.0.0:8000 \
    --preload --timeout ${WORKER_TIMEOUT:-120} \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers ${UVICORN_WORKERS}
