# Monarch-Py

Monarch-Py is a Python library for interfacing with the Monarch Initiative Knowledge graph.  
It can be used from CLI, as a module, or as a FastAPI app

[Documentation](https://monarch-app.monarchinitiative.org/docs)


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
