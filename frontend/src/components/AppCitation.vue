<!--
  citation block of title, authors, and other info
-->

<template>
  <blockquote class="citation">
    <div v-if="title" class="truncate-2" tabindex="0">{{ title }}</div>
    <div v-if="authors" class="truncate-2" tabindex="0">{{ authors }}</div>
    <AppMarkdown
      v-if="detailsString"
      class="truncate-2"
      tabindex="0"
      :source="detailsString"
    />
  </blockquote>
</template>

<script setup lang="ts">
import { computed } from "vue";

type Props = {
  /** work title */
  title?: string;
  /** list of authors */
  authors?: string;
  /** journal, issue, date, or other misc info */
  details?: string[];
}

const props = defineProps<Props>();

/** joined details as string */
const detailsString = computed(() =>
  (props.details || []).filter((e) => e).join("&nbsp; · &nbsp;")
);
</script>

<style lang="scss" scoped>
.citation {
  display: flex;
  flex-direction: column;
  gap: 10px;

  & > div {
    &:nth-child(1) {
      font-weight: 600;
    }

    &:nth-child(2) {
      font-style: italic;
    }
  }
}
</style>
