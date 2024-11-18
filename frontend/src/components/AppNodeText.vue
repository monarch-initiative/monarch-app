<!--
  The text of a node in the knowledge graph. Specially renders any text wrapped
  in <sup> as superscripted in HTML and SVG.
-->

<template>
  <tspan v-if="isSVG" ref="container">
    {{ text }}
  </tspan>
  <span v-else ref="container">
    {{ text }}
  </span>
</template>

<script setup lang="ts">
import { onMounted, onUpdated, ref } from "vue";

type Props = {
  text: string;
  isSVG?: boolean;
};

const props = withDefaults(defineProps<Props>(), {
  isSVG: false,
});

const container = ref<HTMLSpanElement | SVGTSpanElement | null>(null);

function renderSups(el: HTMLSpanElement | SVGTSpanElement) {
  // State to keep track if the current last element in the child nodes is
  // superscripted. (This is necessary because the `dy` attribute affects
  // the current and next sibling <tspan> elements).
  let svgCurrentlySup = false;

  const text = props.text;

  const containsOnlyText =
    el.childNodes.length === 1 &&
    el.firstChild?.nodeType === Node.TEXT_NODE &&
    text !== null;

  // This should always be false, but just in case-- bail out of the function
  // if the element contains anything but a single text node.
  if (!containsOnlyText) return;

  const regex = /<sup>(.*?)<\/sup>/g;
  const newChildren: Node[] = [];

  let idx = 0;

  // Add text to the list of new child nodes. For SVG, this is a <tspan>
  // element. For HTML, it's a TextNode.
  const addText = (text: string) => {
    if (props.isSVG) {
      const el = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "tspan",
      );
      el.textContent = text;

      // If the last <tspan> was superscripted (i.e. has dy="-1ex", then return
      // the text to the normal baseline.
      if (svgCurrentlySup) {
        el.setAttribute("dy", "+1ex");
        svgCurrentlySup = true;
      }

      newChildren.push(el);
    } else {
      newChildren.push(new Text(text));
    }
  };

  for (const match of text.matchAll(regex)) {
    const [outer, inner] = match;

    const startText = text.slice(idx, match.index);

    // If there is text before the match, add it as a text node.
    if (startText) {
      addText(startText);
    }

    const newNode = props.isSVG
      ? document.createElementNS("http://www.w3.org/2000/svg", "tspan")
      : document.createElement("sup");

    newNode.textContent = inner;
    newChildren.push(newNode);

    if (props.isSVG) {
      newNode.classList.add("svg-superscript");
    }

    // If the baseline isn't currently superscripted, move the baseline up.
    if (!svgCurrentlySup) {
      newNode.setAttribute("dy", "-1ex");
      svgCurrentlySup = true;
    }

    // Advance the current index to the end of the match.
    idx += match.index + outer.length;
  }

  // Add any remaining text beyond the match.
  const remainingText = text.slice(idx);

  if (remainingText) {
    addText(remainingText);
  }

  el.replaceChildren(...newChildren);
}

onMounted(() => {
  if (!container.value) return;
  renderSups(container.value);
});

onUpdated(() => {
  if (!container.value) return;
  renderSups(container.value);
});
</script>

<style>
.svg-superscript {
  font-size: 0.7rem;
}
</style>
