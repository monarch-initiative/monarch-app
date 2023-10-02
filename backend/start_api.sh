#!/usr/bin/bash 

# before we start, run the oak server in the background...
poetry run python -m src.monarch_py.api.oak_server &

# ...but block while we wait for it to start serving request
./wait-for-it.sh -t 0 ${OAK_SERVER_HOST:-localhost}:${OAK_SERVER_PORT:-18811}

# check for uvicorn workers env var, default to 8
UVICORN_WORKERS=${UVICORN_WORKERS:-8}

# Start the API
poetry run gunicorn src.monarch_py.api.main:app \
    --bind 0.0.0.0:8000 \
    --preload --timeout ${WORKER_TIMEOUT:-120} \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers ${UVICORN_WORKERS}
