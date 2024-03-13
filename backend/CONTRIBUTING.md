# Welcome to the Monarch Initiative

The Monarch Initiative is an extensive knowledge graph and ecosystem of tools made for the benefit of clinicians, researchers, and scientists. The knowledge graph consists of millions of entities – genes, diseases, phenotypes, and many more – imported from dozens of sources. While we have a core development team, we welcome the contributions of the community to help us maintain and improve the knowledge graph and the tools that use it.

This CONTRIBUTING.md is for the monarch-app backend, also refered to as monarch-py, usable as either a python module or a local CLI. 

# Useful Links

- [Monarch Documentation](https://monarch-initiative.github.io/monarch-documentation/) - In addition to the documentation here, we have a separate documentation site that is automatically generated from the codebase, which encompasses the entire Monarch Initiative ecosystem, as well as the release process and other important information.
- [Monarch Py Documentation](https://monarch-initiative.github.io/monarch-app/) - The Monarch Py documentation contains information on the Python library for interacting with the Monarch Initiative knowledge graph, as well as the FastAPI module that serves as the website's backend.
- [Monarch App Website](https://next.monarchinitiative.org/) - The Monarch Initiative website, a Vue web app using `monarch-py` as the backend.

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
