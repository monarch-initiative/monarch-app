# Welcome to the Monarch Initiative

The Monarch Initiative is an extensive knowledge graph and ecosystem of tools made for the benefit of clinicians, researchers, and scientists. The knowledge graph consists of millions of entities – genes, diseases, phenotypes, and many more – imported from dozens of sources. While we have a core development team, we welcome the contributions of the community to help us maintain and improve the knowledge graph and the tools that use it.

# Table of Contents

- [Useful Links](#important-links)
- [Community Guidelines](#community-guidelines)
- [Monarch App](#monarch-app)
  - [Requirements](#requirements)
    - [Backend Requirements](#backend-requirements)
    - [Frontend Requirements](#frontend-requirements)
    - [Other Requirements](#other-requirements)
  - [Getting Started](#getting-started)
  - [Makefile](#makefile)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Deploying Monarch](#deploying-monarch)

# Useful Links

- [Monarch Documentation](https://monarch-initiative.github.io/monarch-documentation/) - In addition to the documentation here, we have a separate documentation site that is automatically generated from the codebase, which encompasses the entire Monarch Initiative ecosystem, as well as the release process and other important information.
- [Monarch Py Documentation](https://monarch-initiative.github.io/monarch-app/) - The Monarch Py documentation contains information on the Python library for interacting with the Monarch Initiative knowledge graph, as well as the FastAPI module that serves as the website's backend.
- [Monarch App Website](https://next.monarchinitiative.org/) - The Monarch Initiative website, a Vue web app using `monarch-py` as the backend.

# Community Guidelines

We welcome you to our community! We seek to provide a welcoming and safe development experience for everyone. Please read our [code of conduct](CODE_OF_CONDUCT.md)

# Monarch App

[![documentation](https://img.shields.io/badge/-Documentation-purple?logo=read-the-docs&logoColor=white&style=for-the-badge)](https://monarch-initiative.github.io/monarch-documentation/)

[**⭐️⭐️ View the website ⭐️⭐️**](https://next.monarchinitiative.org/)

The monarch-app repository is a monorepo that contains the projects necessary to build and run the web app at monarchinitiative.org and the appropriate tooling and developer resources to continue development. The frontend for the Monarch Initiative website is a javascript/typescript webapp developed using the Vue toolkit. The backend, also referred to as `monarch-py`, is a Python library for interacting with the Monarch Initiative knowledge graph. The `monarch-py` backend also includes an optional FastAPI module that serves as the website's backend and related services for enabling the frontend.

## Requirements

The Monarch Initiative website tool chain has a few requirements that you may need to install before we are ready to work on testing or development. Here is the list of requirements and what they are used for. If you are only working on a portion of the code-base you may not need all of the tools below.

### Backend Requirements

- Python - Most of us use Python version 3.10.12 for development and try to be compatible with versions 3.9-3.12.
- [Poetry](https://python-poetry.org/docs/#installation) - We use Poetry to manage dependencies in `monarch-py`
- pyenv (suggested) - I recommend using pyenv to manage your Python version within different projects

### Frontend Requirements

- Node - The monarch-app frontend is developed in typescript/javascript using Node.js
- Yarn - We use yarn for package management in node environment.
- nvm - I recommend

### Other Requirements

- Docker - Image files used for development and testing for both frontend and backend (required for Solr)
- Rust (cargo) - Required for running the semsimian server locally

## Getting Started

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

### Makefile

The monarch-app repo uses a Makefile system to facilitate and simplify some of the development setup and deployment tasks. For detailed information on the build targets and details of implementation please refer to the `Makefile` in the monarch-app directory.

For a quick-start, once the requirements above are met you can install and launch a working local version of the Monarch App with the following commands.

```shell
cd monarch-app
make install
monarch solr download
monarch solr start
cd frontend
yarn dev
```

Once these commands are run you should have a working version of the Monarch App running from your local system.
_Note_: You may have to resolve some permissions issues with solr in order to download and start monarch solr.

#### Testing

In order to perform testing a few more steps may be needed.

## Backend

For detailed information on running the backend please refer to the [README.md](./backend/README.md) and [CONTRIBUTING.md](./backend/CONTRIBUTING.md) file in the backend directory. Additional information can be find in the [documentation](https://monarch-app.monarchinitiative.org)

## Frontend

# Deploying to Monarch

For documentation on deploying to monarch please see the [Monarch documentation](https://monarch-initiative.github.io/monarch-documentation/release-process/) regarding the release process.
