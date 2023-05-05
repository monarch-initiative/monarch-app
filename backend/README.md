# Monarch Backend

This is a FastAPI for browsing the knowledge graph produced by the Monarch Initiative.

[Documentation](https://monarch-initiative.github.io/monarch-app/docs)

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

#### Planning board:

base_url = https://monarch-initiative.org/api

nodes:

- <s>base_url/entity/{id}</s>
- base_url/entity/{id}/{type of node}

edges:

- ~~base_url/association/{id}~~
- base_url/association/type/{association_type}
- base_url/association/to/{object}
- base_url/association/from/{subject}
- base_url/association/between/{subject}/{object}
- base_url/association/find/{subject_category}
- base_url/association/find/{subject_category}/{object_category}
