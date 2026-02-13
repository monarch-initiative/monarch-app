# This Dockerfile is used to build the Docker image for the Monarch API.
# It assumes that the build context is the root of the repository.
# From the root of the repository, i.e. .../monarch-app:
#   docker build -f backend/Dockerfile .

###############################################
# Base Image
###############################################
FROM python:3.12-slim AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="/root/.local/bin/:$PATH"

###############################################
# Builder Image
###############################################
FROM python-base AS builder-base

RUN apt-get update -y && \
    apt-get install --no-install-recommends -y \
    curl build-essential apt-utils

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY . /opt/monarch-app/

RUN curl -LsSf https://astral.sh/uv/install.sh | sh


###############################################
# Production Image
###############################################

FROM builder-base AS production
ENV SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True
# ENV UVICORN_WORKERS=8
WORKDIR /opt/monarch-app/backend

RUN ls -l . && \
    uv venv && \
    uv pip install .[dev]

CMD /opt/monarch-app/backend/start_api.sh

### Image URLs for reference ###
#   us-central1-docker.pkg.dev/monarch-initiative/monarch-initiative/monarch-api-test:0.1 
#   us-central1-docker.pkg.dev/monarch-initiative/monarch-initiative/monarch-api:0.1
