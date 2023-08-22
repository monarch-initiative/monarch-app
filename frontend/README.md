# Monarch Frontend

This project was scaffolded using Vite (`yarn create vite` → `Vue` → `create-vue`) with the following options:

- TypeScript (for type checking)
- Vue Router (for SPA navigation)
- Vitest (unit testing)
- Playwright (e2e testing)
- ESLint (code quality)
- Prettier (code formatting)

Techniques/approaches used:

- Vue 3
- Composition API
- `<script setup lang="ts">` syntax
- `<style lang="scss" scoped>` styles

## Requirements

- Node `v18` or later
- Yarn `v1` (classic)

## Commands

| Command                  | Description                               |
| ------------------------ | ----------------------------------------- |
| `yarn install`           | Install packages                          |
| `yarn dev`               | Start local dev server with hot-reloading |
| `yarn build`             | Build production version of app           |
| `yarn preview`           | Serve built version of app                |
| `yarn lint`              | Check linting and formatting, _and fix_   |
| `yarn test`              | Run all tests below sequentially          |
| `yarn test:types`        | Type-check codebase                       |
| `yarn test:lint`         | Check linting and formatting              |
| `yarn test:unit`         | Run unit tests with Vitest                |
| `npx playwright install` | Install browsers for Playwright           |
| `yarn test:e2e`          | Run e2e (and Axe) tests with Playwright   |

Custom e2e commands:

```
yarn test:e2e example.spec.ts
yarn test:e2e --project=chromium
yarn test:e2e --debug
```

## Flags

The frontend has a few "flags" that allow you to easily switch certain high-level development settings.

URL parameter flags can be used to set and override a setting at "run time", when opening the webapp.
These flags stay until you refresh the page or open a new tab.
For example, add `?flag=value` to a URL like `monarchinitiative.org/?unrelated-param=123&flag=value`.

Environment variable flags can be used to set/override a setting at "compile time", when building the webapp.
These flags always have to be prefixed with `VITE_`.
For example, set an env var before a command like `VITE_FLAG=value yarn dev`, or add it to `.env` or `.env.local` like `VITE_FLAG=value`.

**`api`**

Which version of the Monarch API to utilize in the frontend, e.g.:

URL param: `monarchinitiative.org/?api=dev`  
Env var: `VITE_API=local`

If not set, inferred from URL.
Flag gets directly inserted into the API URL like `api-beta.monarchinitiative.org`.
See `src/api/index.ts` for related logic.

**`mock`**

Whether to use a real API, or to use a "mock" API where the data returned for each call is always the same set of hard-coded fake/demo JSON.

URL param: `monarchinitiative.org/?mock=true`  
Env var: `VITE_MOCK=true`

Defaults to `false`.

### Style guidelines

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
