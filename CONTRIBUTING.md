# Welcome to the Monarch Initiative

The Monarch Knowledge Graph (Monarch KG) is an extensive knowledge graph and ecosystem of tools made for the benefit of clinicians, researchers, and scientists. The knowledge graph consists of millions of entities – genes, diseases, phenotypes, and many more – imported from dozens of sources. While we have a core development team, we welcome the contributions of the community to help us maintain and improve the knowledge graph and the tools that use it.

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
  - [Quick Start](#quick-start)
- [Testing and Development](#testing-and-development)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Deploying Monarch](#deploying-monarch)

# Useful Links

- [Monarch-KG and Tools Documentation](https://monarch-app.monarchinitiative.org/) - The Monarch KG and tools documentation site includes information about the Monarch-KG and it's access tools, as well as the release process and other important information.
- [Monarch App Website](https://monarchinitiative.org/) - The Monarch-KG website, a Vue web app using `monarch-py`(API) as the backend.
- [Monarch Initiative Documentation](https://monarch-initiative.github.io/monarch-documentation/) - This is the Monarch Initiative's Consortium wide documenation. 

# Community Guidelines

We welcome you to our community! We seek to provide a welcoming and safe development experience for everyone. Please read our [code of conduct](CODE_OF_CONDUCT.md) and reach out to us if you have any questions. We welcome your input!

# Monarch App

[![documentation](https://img.shields.io/badge/-Documentation-purple?logo=read-the-docs&logoColor=white&style=for-the-badge)](https://monarch-app.monarchinitiative.org/)

[**⭐️⭐️ View the website ⭐️⭐️**](https://monarchinitiative.org/)

The monarch-app repository is a monorepo that contains the projects necessary to build and run the web app at monarchinitiative.org and the appropriate tooling and developer resources to continue development. The frontend for the Monarch Initiative website is a javascript/typescript webapp developed using the Vue toolkit. The backend, also referred to as `monarch-py`, is a Python library for interacting with the Monarch Initiative knowledge graph. The `monarch-py` backend also includes an optional FastAPI module that serves as the website's backend and related services for enabling the frontend.

## Requirements

The Monarch Initiative website tool chain has a few requirements that you may need to install before we are ready to work on testing or development. Here is the list of requirements and what they are used for. If you are only working on a portion of the code-base you may not need all of the tools below.

### Backend Requirements

- Python - Most of us use Python version 3.10.12 for development and try to be compatible with versions 3.10 - 3.12.
- [uv](https://docs.astral.sh/uv/) - We use `uv` to manage dependencies in `monarch-py`
- [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation) (suggested) - I recommend using pyenv to manage your Python version within different projects

### Frontend Requirements

- [Bun](https://bun.sh/docs/installation) - Bun is used as a drop-in replacement for Node (non-browser JavaScript runtime environment) and Yarn (package manager). If you already have Node.js installed you Bun will not conflict with your Node.js environment and can be installed as a module. The frontend/CONTRIBUTING.md has simple instructions on how to install Bun.

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

When the new virtual environment is created, you may want to do some peronal modifications to the envoronment. I edit the `activate` script to name the virtual environment more meaningfully and also install `uv` locally (my preference, `activate` then run `pip install uv`). After the virtual environment is set up you will want to start it before each development session by running `activate` (or in your IDE). To exit the environment run `deactivate`.

### Makefile

The monarch-app repo uses a Makefile system to facilitate and simplify some of the development setup and deployment tasks. For detailed information on the build targets and details of implementation please refer to the [Makefile](Makefile) in the monarch-app directory.

### Quick Start
For a quick-start, once the requirements above are met you can install and launch a working local version of the Monarch App with the following commands.

```shell
cd monarch-app
make install
monarch solr download
monarch solr start
cd frontend
bun run dev
```

Once these commands are run you should have a working version of the Monarch App running from your local system.
_Note_: You may have to resolve some permissions issues with solr in order to download and start monarch solr.

# Testing and Development

## Backend

For detailed information the backend please refer to the [README.md](./backend/README.md) and [CONTRIBUTING.md](./backend/CONTRIBUTING.md) file in the backend directory. Additional information can be find in the [documentation](https://monarch-initiative.github.io/monarch-documentation/)

## Frontend

More detailed information on frontend development and run options can be found at the [frontend README.md](./frontend/README.md) and [CONTRIBUTING.md](./frontend/CONTRIBUTING.md) files in the frontend directory. Additional information can be found in the [documentation](https://monarch-initiative.github.io/monarch-documentation/)

# Deploying to Monarch

For documentation on deploying to monarch please see the [Monarch documentation](https://monarch-app.monarchinitiative.org/release-process/) regarding the release process.
