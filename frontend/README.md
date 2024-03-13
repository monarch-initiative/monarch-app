# Monarch Frontend

The monarch-app Frontend is a javascript/typescript app built on the Node.js using Bun for package management. It is developed using the Vue 3 framework and built to be deployed using Docker to Google Cloud Platform to run the Monarch App Website.

You can use the monarch-app frontend to query the Monarch KG using the web app locally. Without additional setup this will use the same FastAPI backend and data source as the website. If you simply want to query the current release of the Monarch KG you probably just want to use the web application directly.

If you want to use a local data store please review the monarch-app README.md and CONTRIBUTING.md in the top level directory of this repository to understand how to manage the whole stack locally.

# Useful Links
- [Monarch App Website](https://next.monarchinitiative.org/) - The Monarch Initiative website, a Vue webapp accessing `monarch-py`, a Python library for interacting with the Monarch Initiative knowledge graph, which includes an optional FastAPI module that serves as the website's backend.
- [Documentation](https://monarch-initiative.github.io/monarch-documentation/) - In addition, to the documentation here, we have a separate documentation site that is automatically generated from the codebase.

## Requirements

- [Bun](https://bun.sh/)

Bun is used as a drop-in replacement for Node (non-browser JavaScript runtime environment) and Yarn (package manager).
It is _not_ yet used as a replacement for Vite (dev previewing, bundling, building) or Vitest (test runner).

It also should make installs (which impact GitHub Actions quota) much faster, and anything that runs locally (like Vite and Vitest) a bit faster as well. Anything that works in Node should also work in Bun, per Bun's stated goals.

To install Bun with an existing Node.js environment (currently recommended for version/package isolation):
```
npm install -g bun
```

If you don't have an existing Node.js implementation and want to install Bun globally on your system (requires curl):
```
curl -fsSL https://bun.sh/install | bash
```

## Quick Start
Once Bun is installed, you will need to install all of the necessary javascript/typescript packages then you can run the dev version from your local repository.

```
bun install
bun run dev
```

You should now be able to run the Monarch Web App from your local system using the Monarch Cloud-Hosted FastAPI and the current realease of the Monarch-KG. If you are trying to use self-hosted data please refer to the README.md in the top-level of the monarch-app repository.

## Commands
Here are some useful commands got using the local Monarch Web App frontend with the current development environment.

| Command                   | Description                               |
| ------------------------- | ----------------------------------------- |
| `bun install`             | Install packages                          |
| `bun run dev`             | Start local dev server with hot-reloading |
| `bun run build`           | Build production version of app           |
| `bun run preview`         | Serve built version of app                |

For more detailed information including test/linting and development please refer to the CONTRIBUTING.md file in this diretory.

# Developers
For detailed information on development of the Monarch Web App please see the CONTRIBUTING.md file in the frontend directory. If you want to use locally hosted data or run the FastAPI locally on your system you should refer to the README.md and CONTRIBUTING.md in the top-level of the monarch-app repository.