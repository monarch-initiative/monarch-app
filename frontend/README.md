# Monarch Frontend

This project was scaffolded using Vite (`bun create vite` → `Vue` → `create-vue`).

Stack summary:

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

## Requirements

- [Bun](bun.sh)

Bun is used as a drop-in replacement for Node (non-browser JavaScript runtime environment) and Yarn (package manager).
It is _not_ yet used as a replacement for Vite (dev previewing, bundling, building) or Vitest (test runner).

This makes one less thing for developers to install.
It also should make installs (which impact GitHub Actions quota) much faster, and anything that runs locally (like Vite and Vitest) a bit faster as well.

Anything that works in Node should also work in Bun, per Bun's stated goals.
Do not use Bun-specific APIs.
If there is ever a problem with Bun, switching back to Node should be as simple as replacing "bun" with "node"/"yarn" and "bunx" with "npx" in commands.

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

See `src/api/index.ts` for logic.

**`mock`**

Whether to use a real API, or to use a "mock" API where the data returned for each call is always the same set of hard-coded fake/demo JSON.

URL param: `monarchinitiative.org/?mock=true`  
Env var: `VITE_MOCK=true`

Defaults to `false`.

## Phenogrid

The pages at `monarchinitiative.org/phenogrid-search` and `monarchinitiative.org/phenogrid-multicompare` provide a widget embeddable on any site via an `<iframe>`.
The widget displays a visual comparison between two sets of phenotypes, and calculates the most and least similar pairs.

Include the widget on your page like so:

```html
<iframe
  src="https://monarchinitiative.org/phenogrid-MODE?PARAM=VALUE&PARAM=VALUE&PARAM=VALUE"
  title="Phenogrid"
  frameborder="0"
></iframe>
```

### Parameters

The widget accepts several URL parameters that depend on the mode of operation.
See `src/api/phenotype-explorer.ts` groups for enumerated options.

Search:

- `subjects` - Comma-separated list of "subject" phenotype IDs (set A).
- `object-group` - "object" group of phenotypes to compare to (group B).

Multi-compare:

- `subjects` - Comma-separated list of "subject" phenotype IDs (set A).
- `objects`- Multiple comma-separated lists of "object" phenotype IDs (B sets).

Any mode:

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

Emitted when the size of the widget changes and on load.
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
