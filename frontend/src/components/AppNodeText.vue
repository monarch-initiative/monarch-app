<!--
  The text of a node in the knowledge graph.

  Selectively renders the following tags in HTML and SVG:
    - <sup>
    - <i>
    - <b>
    - <a> with an `href` attribute starting with `http`, surrounded in double quotes
-->

<template>
  <foreignObject v-if="isSvg" x="0" y="0" width="100%" height="1.5em">
    <span ref="container" xmlns="http://www.w3.org/1999/xhtml">
      {{ text }}
    </span>
  </foreignObject>
  <span v-else ref="container">
    {{ text }}
  </span>
</template>

<script setup lang="ts">
import { onMounted, onUpdated, ref } from "vue";

type Props = {
  text?: string;
  isSvg?: boolean;
  truncateWidth?: number;
};

const props = withDefaults(defineProps<Props>(), {
  text: "",
  isSvg: false,
  truncateWidth: undefined,
});

const container = ref<HTMLSpanElement | null>(null);

function makeEscapedTagPattern(tagName: string, attrsPattern: string = "") {
  return new RegExp(
    `(&lt;${tagName}${attrsPattern}&gt;)(.*?)(&lt;/${tagName}&gt;)`,
    "g",
  );
}

const replacementPatterns = [
  makeEscapedTagPattern("sup"),
  makeEscapedTagPattern("i"),
  makeEscapedTagPattern("b"),
  makeEscapedTagPattern("a", ' href="http[^"]+"'),
];

function buildDOM(containerEl: HTMLSpanElement) {
  const { truncateWidth, isSvg } = props;

  let html = containerEl.innerHTML;

  replacementPatterns.forEach((pattern) => {
    html = html.replaceAll(
      pattern,
      (match, openTag: string, content: string, closeTag: string) => {
        // Replace &lt; with < and &gt; with > to unescape them
        let unescaped = "";
        unescaped += "<" + openTag.slice(4, -4) + ">";
        unescaped += content;
        unescaped += "<" + closeTag.slice(4, -4) + ">";
        return unescaped;
      },
    );
  });

  containerEl.innerHTML = html;

  // WebKit browsers have strange behavior rendering <sup> tags inside
  // <foreignObject> tags. It seems to be because they use relative
  // positioning to style superscripts, and relative positioning inside
  // <foreignObject> tags doesn't work very well (in WebKit). As a result, the
  // superscripted text shows up at the very top of the SVG, as if it were
  // relatively positioned there.
  //
  // To avoid this, we can change the <sup> tags to <span>s and style them
  // ourselves without using relative positioning.
  if (isSvg) {
    const supTags = [...containerEl.querySelectorAll("sup")];

    supTags.forEach((supTag) => {
      const spanTag = document.createElement("span");
      spanTag.style.verticalAlign = "super";
      spanTag.style.fontSize = "80%";
      spanTag.style.lineHeight = "1.0";

      spanTag.replaceChildren(...supTag.childNodes);
      supTag.parentNode!.replaceChild(spanTag, supTag);
    });
  }

  if (truncateWidth) {
    containerEl.style.display = "inline-block";
    containerEl.style.overflow = "hidden";
    containerEl.style.whiteSpace = "nowrap";
    containerEl.style.textOverflow = "ellipsis";
    containerEl.style.verticalAlign = "top";
    containerEl.style.maxWidth = `${truncateWidth}px`;
  }
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
