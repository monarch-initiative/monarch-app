# This Dockerfile is used to build the Docker image for the Monarch API.
# It assumes that the build context is the root of the repository.
# The image is built using the following command structure:
#  (from the root of the repository, i.e. .../monarch-app)
#  docker build -f backend/Dockerfile .

###############################################
# Base Image
###############################################
FROM python:3.9-slim as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # POETRY_VERSION='1.2.0'  \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

###############################################
# Builder Image
###############################################
FROM python-base as builder-base

RUN apt-get update -y && \
    apt-get install --no-install-recommends -y \
    curl build-essential apt-utils

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY . /opt/monarch-app/

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN curl -sSL https://install.python-poetry.org | python3 && \
    poetry self update

###############################################
# Production Image
###############################################

FROM builder-base as production
ENV SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True
# ENV UVICORN_WORKERS=8
WORKDIR /opt/monarch-app/backend

RUN ls -l . && \
    poetry install

CMD /opt/monarch-app/backend/start_api.sh

### Image URLs for reference ###
#   us-central1-docker.pkg.dev/monarch-initiative/monarch-initiative/monarch-api-test:0.1 
#   us-central1-docker.pkg.dev/monarch-initiative/monarch-initiative/monarch-api:0.1
