# Monarch-Py

[![documentation](https://img.shields.io/badge/-Documentation-purple?logo=read-the-docs&logoColor=white&style=for-the-badge)](https://monarch-initiative.github.io/monarch-app)

Monarch-Py is a Python library for interfacing with the Monarch Initiative Knowledge graph. The monarch-py package can be used from CLI, as a module, or as a FastAPI app.

# Requirements

If you are running the whole monarch-app suite locally you will want to review the [README.md](../README.md) or [CONTRIBUTING.md](../CONTRIBUTING.md) files in the repository root for information on the requirements for monarch-app at large. If you intend to run just the backend for end-user usage or testing you will only need the following prerequisites.

- Python >= 3.10 recommended for development.
- [uv](https://docs.astral.sh/uv/) - For managing dependencies in monarch-py.
- [Docker](https://docs.docker.com/get-docker/) - For running the Solr instance locally.
- [Rust](https://www.rust-lang.org/tools/install) - For running the semsimian server locally.

For development of monarch-py, please refer to the [backend/CONTRUBUTING.md](CONTRIBUTING.md) for additional details.

# Usage

Basic installation can be performed using pip/pipx or your favorite package manager.

```
pip install monarch-py
```

The monarch-py module and CLI use the Monarch-KG using a Solr instance running locally.  
This requires Docker to be installed and running on your computer.

```
monarch solr download
monarch solr start
```

This will download and then run the monarch Solr image locally on port 8983.  
_Note_ You may need to change permissions on the file in order to install and run the Solr container.

```
sudo chgrp -R 8983 ~/.data/monarch
sudo chmod -R g+w ~/.data/monarch
```

To check if Solr is running correctly on your computer you can check you can check using Docker or the monarch CLI.

Using Docker:

```
docker ps
```

For docker you should see output resembling this:

```
66da4aeed48e   solr:8            "docker-entrypoint.s…"   3 weeks ago    Up 5 days    0.0.0.0:8983->8983/tcp, :::8983->8983/tcp   monarch_solr
```

Using the monarch CLI:

```
monarch solr status
```

For the monarch CLI you should see output similar to this:

```
Checking for Solr container...

Found monarch_solr container: 66da4aeed48e7f71241f85f31f1e3366f9255cb53b78f16b13fb79bcfb2b36f2
Container status: running
```

monarch-ingest creates it's own Solr docker instance which mounts its own data output from closurizer and makes it's own Solr artifact.

# Developers

For instructions on how to test monarch-py locally or how to start with developing please see the [CONTRIBUTING.md](../CONTRIBUTING.md) file in the root of the Monarch-App repository.  
For instructions specific to monarch-py (the Monarch-App backend), see the [backend/CONTRIBUTING.md](./CONTRIBUTING.md) file.

## For Developers

### Running the API:

#### Local development:

- Connect to and expose the SOLR database:
  `gcloud compute ssh monarch-solr-dev -- -L 8983:localhost:8983`

- Start the uvicorn server:
  `cd <path-to>/monarch-api && uvicorn main:app --reload`

#### GCP deployment:

- First, connect to the GCP SOLR machine:
  `gcloud compute ssh monarch-api-dev -- -L 8000:localhost:8000`

- Then, start the uvicorn server:
  `nohup uvicorn main:app --reload --host 0.0.0.0 &`

#### Building and using the Docker image:

- Build the docker image:
  `docker build --rm --tag us-central1-docker.pkg.dev/monarch-initiative/monarch-api/monarch-api:{VERSION} . `

- Push the docker image:
  `docker push us-central1-docker.pkg.dev/monarch-initiative/monarch-api/monarch-api:{VERSION}`
