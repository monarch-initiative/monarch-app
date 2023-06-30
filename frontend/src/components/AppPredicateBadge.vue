<!--
  an icon, text, and link for a predicate between nodes in the knowledge graph
-->

<template>
  <span class="predicate">
    <AppIcon class="arrow" :icon="`arrow-${arrowDirection}-long`" />
    {{ startCase(association.predicate.replace("biolink:", "")).toLowerCase() }}
    <AppIcon class="arrow" :icon="`arrow-${arrowDirection}-long`" />
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { startCase } from "lodash";
import type { DirectionalAssociation } from "@/api/model";

type Props = {
  /** current predicate */
  association: DirectionalAssociation;
  /** whether to display arrows vertically */
  vertical?: boolean;
};

const props = defineProps<Props>();

/** direction of arrows */
const arrowDirection = computed(() => {
  if (props.vertical) {
    if (props.association.direction === "outgoing") return "down";
    else return "up";
  } else {
    if (props.association.direction === "outgoing") return "right";
    else return "left";
  }
});
</script>

<style lang="scss" scoped>
.predicate {
  white-space: nowrap;

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
