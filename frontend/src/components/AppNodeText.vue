<!--
  The text of a node in the knowledge graph.

  Selectively renders the following tags in HTML and SVG:
    - <sup>
    - <i>
    - <a> with an `href` attribute surrounded in double quotes

  There are two alternatives to the approach taken here, but neither are
  sufficient.

  1. We could use a sanitizer like [DOMPurify](https://github.com/cure53/DOMPurify)
     to sanitize arbitrary strings, but that would strip out legitimate text
     that an HTML parser might confuse for a tag. An example of such text can be
     found here: <https://github.com/monarch-initiative/monarch-app/issues/887#issuecomment-2479676335>

  2. We could escape the entire string, selectively unescape `&lt;sup&gt;` (and
     so on), and then pass the string to `containerEl.innerHTML`. However, this
     would lead to markup without the desired effect in SVG, since the <sup> and
     <i> elements do not do anything in SVG.

-->

<template>
  <tspan v-if="isSvg" ref="container">
    {{ text }}
  </tspan>
  <span v-else ref="container">
    {{ text }}
  </span>
</template>

<script setup lang="ts">
import { onMounted, onUpdated, ref } from "vue";

type Props = {
  text?: string;
  isSvg?: boolean;
};

const props = withDefaults(defineProps<Props>(), {
  text: "",
  isSvg: false,
});

const container = ref<HTMLSpanElement | SVGTSpanElement | null>(null);

type ReplacedTag = "sup" | "a" | "i";

type Replacement = {
  type: ReplacedTag;
  start: [number, number];
  end: [number, number];
  startNode?: Text;
  endNode?: Text;
};

type ReplacementPosition = {
  type: "start" | "end";
  replacement: Replacement;
  at: [number, number];
};

const replacementTags = new Map([
  [
    "sup" as ReplacedTag,
    {
      regex: /(<sup>).*?(<\/sup>)/dg,
      createSurroundingEl(isSvg: Boolean) {
        return isSvg
          ? document.createElementNS("http://www.w3.org/2000/svg", "tspan")
          : document.createElement("sup");
      },
      afterMount(isSvg: Boolean, el: Element) {
        if (!isSvg) return;
        el.setAttribute("dy", "-1ex");
        el.classList.add("svg-superscript");

        // The next sibling will be the text node "</sup>". Check if there is
        // remaining text after that. If there is, adjust the text baseline back
        // down to the normal level.
        const nextSibling = el.nextSibling!.nextSibling;
        if (!nextSibling) return;

        const range = new Range();
        range.selectNode(nextSibling);

        const tspan = document.createElementNS(
          "http://www.w3.org/2000/svg",
          "tspan",
        );

        tspan.setAttribute("dy", "+1ex");

        range.surroundContents(tspan);
      },
    },
  ],
  [
    "i" as ReplacedTag,
    {
      regex: /(<i>).*?(<\/i>)/dg,
      createSurroundingEl(isSvg: Boolean) {
        return isSvg
          ? document.createElementNS("http://www.w3.org/2000/svg", "tspan")
          : document.createElement("i");
      },
      afterMount(isSvg: Boolean, el: Element) {
        if (!isSvg) return;
        el.classList.add("svg-italic");
      },
    },
  ],
  [
    "a" as ReplacedTag,
    {
      regex: /(<a href="http[^"]+">).*?(<\/a>)/dg,
      createSurroundingEl(isSvg: Boolean) {
        return isSvg
          ? document.createElementNS("http://www.w3.org/2000/svg", "a")
          : document.createElement("a");
      },
      afterMount(isSvg: Boolean, el: Element) {
        // The previous sibling will be the text node containing the string
        // <a href="http...">. Slice it to get the value of the href.
        const tagTextNode = el.previousSibling!;
        const href = tagTextNode.textContent!.slice(9, -2);
        el.setAttribute("href", href);
      },
    },
  ],
]);

function buildDOM(containerEl: Element) {
  const text = props.text;

  const containsOnlyText =
    containerEl.childNodes.length === 1 &&
    containerEl.firstChild?.nodeType === Node.TEXT_NODE &&
    text !== null;

  // This should always be false, but just in case-- bail out of the function
  // if the element contains anything but a single text node.
  if (!containsOnlyText) return;

  const textNode = containerEl.firstChild as Text;

  const replacements: Replacement[] = [];

  // Create a list of every place there's a match for a start and end tag
  // matched from the defined regexes.
  Array.from(replacementTags.entries()).forEach(([type, { regex }]) => {
    for (const match of text.matchAll(regex)) {
      const { indices } = match;

      replacements.push({
        type,
        start: indices![1],
        end: indices![2],
      });
    }
  });

  // Now create a new list that has the position of each start and end token
  const positions: ReplacementPosition[] = replacements.flatMap((x) => [
    { type: "start", replacement: x, at: x.start },
    { type: "end", replacement: x, at: x.end },
  ]);

  // Sort that list by the position of the tag token (with the last token
  // first and the first token last).
  //
  // After that, iterate through each of the token positions and split the
  // text node at the token's boundaries. Store the text node of each start
  // and end tag in the `replacements` array to be used later.
  positions
    .sort((a, b) => {
      return b.at[0] - a.at[0];
    })
    .forEach((position) => {
      textNode.splitText(position.at[1]);
      const node = textNode.splitText(position.at[0]);
      position.replacement[`${position.type}Node`] = node;
    });

  // Build the correct DOM tree for each replacement found
  replacements.forEach((replacement) => {
    const { startNode, endNode, type } = replacement;
    const { createSurroundingEl, afterMount } = replacementTags.get(type)!;

    // Select the range that goes from the end of the opening tag text node to
    // the start of the closing tag text node.
    const range = new Range();
    range.setStartAfter(startNode!);
    range.setEndBefore(endNode!);

    // Surround that range with the appropriate DOM element.
    const el = createSurroundingEl(props.isSvg);
    range.surroundContents(el);

    // Run any code required after the container element is mounted.
    afterMount(props.isSvg, el);

    // Remove the start and end tag text nodes
    startNode!.parentNode!.removeChild(startNode!);
    endNode!.parentNode!.removeChild(endNode!);
  });
}

onMounted(() => {
  if (!container.value) return;
  buildDOM(container.value);
});

onUpdated(() => {
  if (!container.value) return;
  buildDOM(container.value);
});
</script>

<style>
.svg-superscript {
  font-size: 0.7rem;
}
.svg-italic {
  font-style: italic;
}
</style>
