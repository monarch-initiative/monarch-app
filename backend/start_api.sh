#!/usr/bin/bash 

# check for uvicorn workers env var, default to 8
if [ -z "${UVICORN_WORKERS}" ]; then
    UVICORN_WORKERS=8
fi

# Start the API
/opt/poetry/bin/poetry run uvicorn src.monarch_py.api.main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS}
