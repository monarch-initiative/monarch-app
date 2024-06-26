# Phenogrid

A widget for visualizing similarity between phenotypes.

## Overview

Phenogrid displays a visual comparison between sets of phenotypes in a grid arrangement, with calculations of the similarity in various metrics.

Public pages at `monarchinitiative.org/phenogrid-search` and `/phenogrid-multi-compare` provide a widget embeddable on any site via an `<iframe>`, for example:

```html
<iframe
  src="https://monarchinitiative.org/phenogrid-search?PARAM=VALUE&..."
  title="Phenogrid"
  name="some-optional-name"
  frameborder="0"
  width="75%"
  height="600px"
></iframe>
```

You can specify a height and width here, but the widget will emit a `message` event to the parent window with the intrinsic size of its content, so you can dynamically set the dimensions of your iframe container.  
See the [Events](#events) section for more details.

## Modes

Phenogrid can operate in multiple modes, which you can specify via the `src` URL.

- [`/phenogrid-search`](#search-mode) - Compares a list of enumerated phenotypes (set A) against all the phenotypes from a gene or disease of interest (group B).
- [`/phenogrid-multi-compare`](#multi-compare-mode) - Compares a list of enumerated phenotypes to _multiple_ enumerated other lists of phenotypes.

For more details on the parameters for each mode, see the respective sections below.

## Passing Parameters

The widget can accept input parameters in two different ways.
You can choose to pass them either way, unless specified otherwise.

### URL Params (simple)

Specify params in the `src` URL like `?some-param=1,2,3&another-param=abc`.
This is allows convenient use in cases where the parameters are simple and short.

### Message Params (detailed)

For more flexible and detailed parameters, you can omit params from the URL and instead send the widget a message from JavaScript like this:

```js
// get your iframe DOM element somehow
const iframe = document.querySelector("iframe[name='your-iframe-name']");
// send it a message
iframe.contentWindow.postMessage(
  // some parameters
  {
    subjects: ["HP:123,HP:456"],
    "object-group": "Human Diseases",
  },
  // https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage#targetorigin
  "*",
);
```

You should use this method when your params might be [too long for a URL](https://www.google.com/search?q=max+url+length).

## "Search" Mode Parameters

As URL params:

- `subjects` - Comma-separated list of phenotype IDs, e.g. `HP:123,HP:abc,HP:456`.
- `object-group` - Group name, e.g. "Human Diseases".
  See `src/api/phenotype-explorer.ts` for enumerated options.

As message params:

```ts
{
  subjects: string[],
  "object-group": string
}
```

## "Multi-Compare" Mode Parameters

As URL params:

- `subjects` - Comma-separated list of phenotype IDs, e.g. `HP:123,HP:abc,HP:456`.
- `object-sets` - Comma-separated lists of phenotype IDs, e.g. `?object-sets=HP:123,HP:456&object-sets=HP:abc,HP:def`

Pass as message params to control additional details like set labels.

As message params:

```ts
{
  subjects: string[],
  "object-sets": {
    // unique identifier for set
    id: string;
    // human-readable label for set
    label: string;
    // list of phenotype ids
    phenotypes: string[];
  }[]
}
```

If there are no other appropriate values for them, `id` can be a simple incrementing integer and `label` can something simple like "Set A".

#### Emits `MessageEvent<{ name: string; width: number; height: number; }>`

You can use the same event listener as the standard Phenogrid widget to set the dimensions of your iframe container.

## General Parameters

General parameters available regardless of the mode of operation.

- `stylesheet` - URL to a stylesheet that will be applied to the widget, for the purposes of matching its styles to your webpage.
  - If passed as a URL param, make sure it is URI encoded.

## Events

The widget also emits `message` events to the parent window when certain things change.

### Resize

The widget emits a "resize" event when the inherent size of the widget changes, in the form of:

```ts
MessageEvent<{
  // new intrinsic size of content within widget, in pixels
  // (analogous to "max-content" CSS keyword)
  width: number;
  height: number;
  // "name" attribute of iframe that emitted event
  // useful if you have several instances of the widget on your page
  name: string;
}>;
```

This can happen when it switches from loading to results, when new phenotypes are loaded, when the grid is flipped/transposed, etc.

This can be useful for dynamically setting the dimensions of your iframe container:

```js
window.addEventListener("message", (event) => {
  const { name, width, height } = event.data;
  const iframe = document.querySelector(`iframe[name='${name}']`);
  if (!iframe) return;
  // recommended styling...
  // let iframe fill its container
  iframe.style.width = "100%";
  iframe.style.height = "1000px";
  // but never bigger than its contents
  iframe.style.maxWidth = width + "px";
  iframe.style.maxHeight = height + "px";
  // contents will wrap/scroll appropriately at smaller sizes
});
```
