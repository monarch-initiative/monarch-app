<!--
  an icon, text, and link for a predicate between nodes in the knowledge graph
-->

<template>
  <span class="predicate">
    <AppIcon v-if="arrows" class="arrow" :icon="`arrow-${arrowDirection}`" />
    <span v-if="association.negated" class="negated-text">NOT</span>

    <span v-html="highlightedPredicate"></span>
    <AppIcon v-if="arrows" class="arrow" :icon="`arrow-${arrowDirection}`" />
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { startCase } from "lodash";
import { getCategoryLabel } from "@/api/categories";
import { type DirectionalAssociation } from "@/api/model";

type Props = {
  /** current association */
  association: Partial<DirectionalAssociation>;
  /** whether to reverse the direction of arrows */
  reverse?: boolean;
  /** whether to display arrows vertically */
  vertical?: boolean;
  arrows?: boolean;
  /** search term for highlighting */
  search?: string;
};

const props = defineProps<Props>();

/** direction of arrows */
const arrowDirection = computed(() =>
  props.reverse
    ? props.vertical
      ? "up"
      : "left"
    : props.vertical
      ? "down"
      : "right",
);

const highlightedPredicate = computed(() => {
  const predicateLabel = startCase(
    getCategoryLabel(props.association.predicate),
  ).toLowerCase();

  if (!props.search) {
    return predicateLabel; // No search term, return the original text
  }

  const searchRegex = new RegExp(props.search, "gi"); // Case-insensitive search
  return predicateLabel.replace(
    searchRegex,
    (match) => `<span class="highlight">${match}</span>`,
  );

  // return predicateLabel.replace(
  //   searchRegex,
  //   (match) => `<span style="
  //   background: yellow;">${match}</span>`,
  // );
});
</script>

<style lang="scss" scoped>
.predicate {
  & > * {
    white-space: normal;
    overflow-wrap: anywhere;
  }
}

.arrow {
  color: $gray;

  &:first-child {
    margin-right: 0.5em;
  }

  &:last-child {
    margin-left: 0.5em;
  }
}
:deep(.highlight) {
  background: yellow;
}
.negated-text {
  color: $error;
  font-weight: 600;
}
</style>
