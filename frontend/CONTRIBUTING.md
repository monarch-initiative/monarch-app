# Welcome to the Monarch Initiative

The Monarch Initiative is an extensive knowledge graph and ecosystem of tools made for the benefit of clinicians, researchers, and scientists. The knowledge graph consists of millions of entities – genes, diseases, phenotypes, and many more – imported from dozens of sources. While we have a core development team, we welcome the contributions of the community to help us maintain and improve the knowledge graph and the tools that use it.

This CONTRIBUTING.md is a javascript/typescript web app using Bun as a replacement for Node.js (a non-browser JavaScript runtime environment) with the Vite/Vue framework. You can use the monarch-app frontend to query the Monarch KG using the web app locally.

Without additional setup this will use the same FastAPI backend and data source as the website. This is primarily for front-end development of the website UI. If you want to use a local data store review the monarch-app README.md and CONTRIBUTING.md in the top level directory of this repository to understand how to manage the whole stack locally.

# Useful Links

- [Monarch App Website](https://next.monarchinitiative.org/) - The Monarch Initiative website, a Vue webapp accessing `monarch-py`, a Python library for interacting with the Monarch Initiative knowledge graph, which includes an optional FastAPI module that serves as the website's backend.
- [Documentation](https://monarch-initiative.github.io/monarch-documentation/) - In addition, to the documentation here, we have a separate documentation site that is automatically generated from the codebase.

# Table of Contents

- [Welcome to the Monarch Initiative](#welcome-to-the-monarch-initiative)
- [Useful Links](#useful-links)
- [Quick Start](#quick-start)
  - [Dependancies](#dependancies)
- [Monarch Frontend Details](#monarch-frontend-details)
  - [Commands](#commands)
  - [Flags](#flags)
  - [Phenogrid](#phenogrid)
    - [Parameters](#parameters)
    - [Events](#events)
  - [Style guidelines](#style-guidelines)

# Quick Start

To get started running or testing the frontend environment, install the dependancies then

## Dependancies

- [Bun](bun.sh)

Bun is used as a drop-in replacement for Node (non-browser JavaScript runtime environment) and Yarn (package manager).
It is _not_ yet used as a replacement for Vite (dev previewing, bundling, building) or Vitest (test runner).

This makes one less thing for developers to install.
It also should make installs (which impact GitHub Actions quota) much faster, and anything that runs locally (like Vite and Vitest) a bit faster as well.

Anything that works in Node should also work in Bun, per Bun's stated goals.
Do not use Bun-specific APIs.
If there is ever a problem with Bun, switching back to Node should be as simple as replacing "bun" with "node"/"yarn" and "bunx" with "npx" in commands.

To install Bun with an existing Node.js environment (currently recommended for version/package isolation):

```
npm install -g bun
```

If you don't have an existing Node.js implementation and want to install Bun globally on your system (requires curl):

```
curl -fsSL https://bun.sh/install | bash
```

## Run using Monarch Cloud hosted API

To run the frontend using the Monarch Cloud hosted API, you can use the following commands:

```
bun install
bun run dev
```

You should now be able to run the Monarch Web App from your local system using the Monarch Cloud-Hosted FastAPI and the current realease of the Monarch-KG. If you are trying to use self-hosted data please refer to the README.md in the top-level of the monarch-app repository.

## Run using local API from backend

To host the API locally using the backend development in this repo first see frontend/README.md and frontend/CONTRIBUTING.md to ensure dependencies and requirements are met. Once requirements are met you can run the following commands to run the Monarch Web App frontend using the current development backend.

```
cd ../backend
poetry install
poetry run monarch solr download
```

_Note_ You may need to change permissions on the file in order to install and run the Solr container.

```
sudo chgrp -R 8983 ~/.data/monarch
sudo chmod -R g+w ~/.data/monarch
```

If the permissions are correct you can then run the Solr instance with:

```
poetry run monarch solr start
```

In a seperate terminal run the API (this will need to stay running will you are using the UI). Go to monarch-app root and run:

```
make dev-api
```

Once the API is properly set up with the above commands you can run the frontend with:

```
cd ../frontend
VITE_API-local bun run dev
```

If you run into problems please see the more detailed information in frontend/README.md and forntend/CONTRIBUTING.md

# Monarch Frontend Details

The monarch-app Frontend is a javascript/typescript app built on the Node.js using Bun for package management. It is developed using the Vue 3 framework and built to be deployed using

This project was scaffolded using Vite (`bun create vite` → `Vue` → `create-vue`).

- Bun (for runtime and package manager, see note below)
- TypeScript (for type checking)
- Vue Router (for SPA navigation)
- Vitest (unit testing)
- Playwright (e2e testing)
- ESLint (code quality)
- Prettier (code formatting)
- Vue 3
- Composition API
- `<script setup lang="ts">` syntax
- `<style lang="scss" scoped>` styles

## Commands

| Command                   | Description                               |
| ------------------------- | ----------------------------------------- |
| `bun install`             | Install packages                          |
| `bun run dev`             | Start local dev server with hot-reloading |
| `bun run build`           | Build production version of app           |
| `bun run preview`         | Serve built version of app                |
| `bun run lint`            | Check linting and formatting, _and fix_   |
| `bun run test`            | Run all tests below sequentially          |
| `bun run test:types`      | Type-check codebase                       |
| `bun run test:lint`       | Check linting and formatting              |
| `bun run test:unit`       | Run unit tests with Vitest                |
| `bunx playwright install` | Install browsers for Playwright           |
| `bun run test:e2e`        | Run e2e (and Axe) tests with Playwright   |

Custom e2e commands:

```
bun run test:e2e example.spec.ts
bun run test:e2e --project=chromium
bun run test:e2e --debug
```

## Flags

The frontend has a few "flags" that allow you to easily switch certain high-level development settings.

URL parameter flags can be used to set and override a setting at "run time", when opening the web app.
These flags stay until you refresh the page or open a new tab.
For example, add `?flag=value` to a URL like `monarchinitiative.org/?unrelated-param=123&flag=value`.

Environment variable flags can be used to set/override a setting at "compile time", when building the web app.
These flags always have to be prefixed with `VITE_`.
For example, set an env var before a command like `VITE_FLAG=value bun dev`, or add it to `.env` or `.env.local` like `VITE_FLAG=value`.

**`api`**

Which version of the Monarch API to utilize in the frontend, e.g.:

URL param: `monarchinitiative.org/?api=dev`  
Env var: `VITE_API=local`

For example, to use the an API running local you can run:

```
VITE_API=local bun run dev
```

See `src/api/index.ts` for logic.

**`mock`**

Whether to use a real API, or to use a "mock" API where the data returned for each call is always the same set of hard-coded fake/demo JSON.

URL param: `monarchinitiative.org/?mock=true`  
Env var: `VITE_MOCK=true`

Defaults to `false`.

## Phenogrid

The page at `monarchinitiative.org/phenogrid` provides a widget embeddable on any site via an `<iframe>`.
The widget displays a visual comparison between two sets of phenotypes, and calculates the most and least similar pairs.

Include the widget on your page like so:

```html
<iframe
  src="https://monarchinitiative.org/phenogrid?PARAM=VALUE&PARAM=VALUE&PARAM=VALUE"
  title="Phenogrid"
  frameborder="0"
></iframe>
```

### Parameters

The widget accepts several URL parameters:

- `source` - Comma-separated list of "source" phenotype IDs (set A).
- `target` - "target" group of phenotypes to compare to (group B).
  See `src/api/phenotype-explorer.ts` groups for enumerated options.
- `stylesheet` - A URI-encoded URL to a stylesheet that will be applied to the widget, for the purposes of matching its styles to your webpage.

### Events

The widget also emits `message` events to the parent window when certain things change, and listens for `message` events from the parent window to receive information.

#### Listens for `MessageEvent<{ source: string[], target: string }>`

Provide input phenotype lists to the widget when they might be [too long for a URL](https://www.google.com/search?q=max+url+length).

```js
// get your iframe dom element somehow
const iframe = document.querySelector("iframe");
// send it a message
iframe.contentWindow.postMessage(
  {
    subjects: ["HP:123,HP:456"],
    "object-group": "Human Diseases",
  },
  "*",
);
```

#### Emits `MessageEvent<{ name: string; width: number; height: number; }>`

Useful for setting the dimensions of your iframe container.
Passes back the name attribute of the iframe that emitted the event.
Example:

```js
window.addEventListener("message", (event) => {
  const { name, width, height } = event.data;
  const iframe = document.querySelector(`iframe[name='${name}']`);
  if (!iframe) return;
  iframe.style.maxWidth = width + "px";
  iframe.style.maxHeight = height + "px";
});
```

## Style guidelines

Use JSDoc style comments (`/** some comment */`) instead of regular JavaScript comments.
This allows lint checking and auto-fixing/auto-formatting of long comments wrapping to new lines.
More importantly, it allows for better editor integration.
Hovering over a function/parameter/object/etc. will show the JSDoc comment from above where it was defined.
You can use snippets/shortcuts/extensions/etc. to make this as convenient as regular comments.

Where possible and appropriate, use custom components like `AppHeading` and `AppLink` instead of native elements like `h1` and `a`.

See `variables.scss` for a palette of acceptable colors/fonts/etc to use.

Keep configuration files as minimal as possible and conform to third-party-maintained presets.
For example, avoid overriding default ESLint rules as much as possible.

Keep long lists, such as those in `/global`, sorted alphabetically for consistency and ease of lookup and comparison.

Use `console.log` for strictly for temporary debugging during local development that should be removed before merging PRs.
Use `console.error` for in-production logging of _caught_ errors.
Use `console.warn` for in-production logging of events that are not problems, but are still useful to know.
Use `console.info` for generic in-production logging.

Only log major, infrequent events.
Logging too frequently (say, multiple times per second, sustained) can impact page performance.
Leaving select logging in production will be beneficial for in this particular app, for user and in-situ troubleshooting of complex, hard-to-replicate problems.

To analyze the size of the compiled bundle, dev-install `stats-webpack-plugin`, uncomment the `stats-webpack-plugin` line in `vue.config.js`, build the app, then run either `npx webpack-bundle-analyzer dist/stats.json` or `npx source-map-explorer dist/js/*`.

To spell check the entire repo (aside from `node_modules`), run `npx cspell "**/*.{scss,js,ts,json,vue,svg,yaml}"`.

For consistency, use Prettier to format whatever you can.
Some of the things it can format: `.js`, `.ts`, `.vue`, `.html`, `.svg`, `.yaml`, `.json`, `.md`, etc.
