# Welcome to the Monarch Initiative

The Monarch Initiative is an extensive knowledge graph and ecosystem of tools made for the benefit of clinicians, researchers, and scientists. The knowledge graph consists of millions of entities – genes, diseases, phenotypes, and many more – imported from dozens of sources.

We welcome the contributions of the community to help us maintain and improve the knowledge graph and the tools that use it. To help get started on contributing to the Monarch Initiative, please see our [CONTRIBUTING.md](./CONTRIBUTING.md) file.

# Monarch App

[![documentation](https://img.shields.io/badge/-Documentation-purple?logo=read-the-docs&logoColor=white&style=for-the-badge)](https://monarch-app.monarchinitiative.org/)  
![](https://github.com/monarch-initiative/monarch-app/actions/workflows/test-backend.yaml/badge.svg)
![](https://github.com/monarch-initiative/monarch-app/actions/workflows/test-frontend.yaml/badge.svg)
![](https://github.com/monarch-initiative/monarch-app/actions/workflows/deploy-documentation.yaml/badge.svg)
![](https://github.com/monarch-initiative/monarch-app/actions/workflows/build-image.yaml/badge.svg)

[**⭐️⭐️ View the website ⭐️⭐️**](https://next.monarchinitiative.org/)

The monarch-app repo contains the source code for the Monarch Initiative website (a Vue webapp),  
as well as `monarch-py`, a Python library for interacting with the Monarch Initiative knowledge graph. The `monarch-py` library also includes a FastAPI module that serves as the website's backend. Together, the frontend and backend make up the stack used to deply and run the Monarch Initiative website.

If you wish to run Monarch-App as a local web application, please install the requirements below and then follow on to the usage section to start the application. Refer to [Using Local Data](#using-local-data) to see how you can run the full Monarch website locally and use your own data store.

The app also offers a widget called Phenogrid that can be embedded in any website.  
For more information on how to use the Phenogrid widget, please refer to the [Phenogrid documentation](./frontend/PHENOGRID.md).

### For developers

The monarch-app repository contains the code to run the Monarch Initiative website in the `frontend` and `backend` directories as well as documentation, helper scripts, Docker files and services to help set up a local environment for development and for deployment.

To start development, please refer to the [CONTRIBUTING.md](./CONTRIBUTING.md) document with this README. If you are planning to only develop the frontend or backend of the application you can refer directly to the README and CONTRIBUTING files in each of those sections.
