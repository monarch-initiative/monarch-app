# Welcome to the Monarch Initiative

The Monarch Initiative is an extensive knowledge graph and ecosystem of tools made for the benefit of clinicians, researchers, and scientists. The knowledge graph consists of millions of entities – genes, diseases, phenotypes, and many more – imported from dozens of sources. While we have a core development team, we welcome the contributions of the community to help us maintain and improve the knowledge graph and the tools that use it.

# Table of Contents

- [Useful Links](#important-links)
- [Monarch App](#monarch-app)
  - [Getting Started](#for-developers)
  - [Using Makefile](#using-makefile)
  - [Running the backend](#running-the-backend)
  - [Running the frontend](#running-the-frontend)
- [Deploying Monarch](#deploying-monarch)
  - [Deploying to Dev](#deploying-to-dev)
  - [Deploying to Beta](#deploying-to-beta)
  - [Deploying to Prod](#deploying-to-prod)

# Useful Links
- [Documentation](https://monarch-initiative.github.io/monarch-documentation/) - In addition, to the documentation here, we have a separate documentation site that is automatically generated from the codebase.
- [Monarch App Website](https://next.monarchinitiative.org/) - The Monarch Initiative website, a Vue webapp accessing `monarch-py`, a Python library for interacting with the Monarch Initiative knowledge graph, which includes an optional FastAPI module that serves as the website's backend.

# Monarch App
    
[![documentation](https://img.shields.io/badge/-Documentation-purple?logo=read-the-docs&logoColor=white&style=for-the-badge)](https://monarch-initiative.github.io/monarch-documentation/)

[**⭐️⭐️ View the website ⭐️⭐️**](https://next.monarchinitiative.org/)

The monarch-app repository is a monorepo that contains the projects necessary to build and run the web app at monarchinitiative.org and the appropriate tooling and developer resources to continue development. The frontend for the Monarch Initiative website is a javascript/typescript webapp developed using the Vue toolkit. The backend, also referred to as `monarch-py`, is a Python library for interacting with the Monarch Initiative knowledge graph. The `monarch-py` backend also includes an optional FastAPI module that serves as the website's backend and related services for enabling the frontend.

## Getting started
To get started with development in monarch-app clone the repo and navigate to the directory.

  ```shell
  git clone git@github.com:monarch-initiative/monarch-app.git
  cd monarch-app
  ```

In order to maintain a clean system environment you may want to create a local python environment. I also recommend setting a local python version of 3.10 with pyenv. You can do both with the following commands.

  ```shell
  pyenv install 3.10.12
  pyenv local 3.10.12
  python -m venv .venv
  ```

When the new virtual environment is created, you may want to do some peronal modifications to the envoronment. I edit the `activate` script to name the virtual environment more meaningfully and also install `poetry` locally (my preference, `activate` then run `pip install poetry`). After the virtual environment is set up you will want to start it before each development session by running `activate` (or in your IDE). To exit the environment run `deactivate`.

### Using Makefile
The monarch-app repo uses a Makefile system to facilitate and simplify some of the development setup and deployment tasks. For detailed information on the build targets and details of implementation please refer to the `Makefile` in the monarch-app directory. 