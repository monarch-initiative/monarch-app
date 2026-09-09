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

- [uv](https://docs.astral.sh/uv/) - We use `uv` to manage both dependencies and the Python interpreter for `monarch-py`
- Python - You do **not** need to install Python yourself. `uv` downloads and manages the interpreter for you, using the version pinned in `backend/.python-version` (currently 3.10). We develop against the oldest supported version and test for compatibility with 3.10 - 3.12.

### Frontend Requirements

- [Bun](https://bun.sh/docs/installation) - Bun is used as a drop-in replacement for Node (non-browser JavaScript runtime environment) and Yarn (package manager). Bun will not conflict with an existing Node.js environment.

Install it with whichever of these suits your setup:

```shell
brew install oven-sh/bun/bun     # macOS
npm install -g bun               # if you already have Node.js
curl -fsSL https://bun.sh/install | bash
```

See [frontend/CONTRIBUTING.md](./frontend/CONTRIBUTING.md) for more detail on how Bun is used in this project.

### Other Requirements

- Docker - Image files used for development and testing for both frontend and backend (required for Solr)
- Rust (cargo) - Required for running the semsimian server locally

## Getting Started

To get started with development in monarch-app clone the repo and navigate to the directory.

```shell
gh repo clone monarch-initiative/monarch-app
cd monarch-app
```

You do not need to create a virtual environment or install a Python version by hand. `make install` (below) delegates to `uv`, which reads the pinned version from `backend/.python-version`, downloads that interpreter if you don't already have it, and creates `backend/.venv` from it.

To run a backend command inside that environment, prefix it with `uv run` from the `backend` directory — for example `uv run pytest tests`. This resolves the environment for you, so there is no `activate` step.

### Makefile

The monarch-app repo uses a Makefile system to facilitate and simplify some of the development setup and deployment tasks. For detailed information on the build targets and details of implementation please refer to the [Makefile](Makefile) in the monarch-app directory.

### Quick Start

Once the requirements above are met, you can install and launch a working local version of the Monarch App with the following steps.

Install the backend and frontend:

```shell
cd monarch-app
make install
```

_Note_: During `make install`, the Playwright browser download step prints `Download failed: server returned code 400` once per browser. This is expected — Playwright's primary CDN has been retired, and it automatically retries against a working mirror. The install succeeded as long as each browser ends with `... downloaded to /Users/<you>/Library/Caches/ms-playwright/...`. See [#1380](https://github.com/monarch-initiative/monarch-app/issues/1380) for the upgrade that removes these retries.

Download and start Solr. The `monarch` CLI is installed into `backend/.venv`, so run it with `uv run`:

```shell
cd backend
uv run monarch solr download
uv run monarch solr start
```

_Note_: `monarch solr download` may end with a message that the Solr container requires write access to its data directory. The container runs as group 8983, so the directory on your machine needs to be group-writable. The CLI prints the exact commands for your path, which look like this:

```shell
sudo chgrp -R 8983 ~/.data/monarch
sudo chmod -R g+w ~/.data/monarch
```

Run those, then re-run the download.

Start the frontend:

```shell
cd ../frontend
bun run dev
```

You should now have a working version of the Monarch App running from your local system, accessible via http://localhost:5173/

# Testing and Development

## Backend

For detailed information the backend please refer to the [README.md](./backend/README.md) and [CONTRIBUTING.md](./backend/CONTRIBUTING.md) file in the backend directory. Additional information can be find in the [documentation](https://monarch-initiative.github.io/monarch-documentation/)

## Frontend

More detailed information on frontend development and run options can be found at the [frontend README.md](./frontend/README.md) and [CONTRIBUTING.md](./frontend/CONTRIBUTING.md) files in the frontend directory. Additional information can be found in the [documentation](https://monarch-initiative.github.io/monarch-documentation/)

# Deploying to Monarch

For documentation on deploying to monarch please see the [Monarch documentation](https://monarch-app.monarchinitiative.org/release-process/) regarding the release process.
