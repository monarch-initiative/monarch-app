<!--
  takes a string of basic markdown and renders html. only use on a per
  paragraph basis. do not put in markdown headings.
-->

<template>
  <component :is="component" v-html="html" />
</template>

<script setup lang="ts">
import { computed } from "vue";
import { micromark } from "micromark";

type Props = {
  /** markdown input source */
  source: string;
  /** what component to wrap source in */
  component?: string;
};

const props = withDefaults(defineProps<Props>(), { component: "div" });

/** html converted from markdown source code */
const html = computed(() =>
  micromark(props.source || "")
    .replaceAll("<p>", "")
    .replaceAll("</p>", "")
);
</script>
