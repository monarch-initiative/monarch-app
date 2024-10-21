<!--
  an icon, text, and link for a predicate between nodes in the knowledge graph
-->

<template>
  <span class="predicate">
    <AppIcon v-if="arrows" class="arrow" :icon="`arrow-${arrowDirection}`" />
    <span v-if="association.negated">NOT</span>
    {{ startCase(getCategoryLabel(association.predicate)).toLowerCase() }}
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
</style>
