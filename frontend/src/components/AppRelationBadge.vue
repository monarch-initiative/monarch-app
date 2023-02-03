<!--
  an icon, text, and link for a relation between nodes in the knowledge graph
-->

<template>
  <span class="relation">
    <AppIcon class="arrow" :icon="`arrow-${arrowDirection}-long`" />
    <AppLink :to="relation.iri" :no-icon="true">{{
      startCase(relation.name)
    }}</AppLink>
    <AppIcon class="arrow" :icon="`arrow-${arrowDirection}-long`" />
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { startCase } from "lodash";
import { Association } from "@/api/node-associations";

interface Props {
  /** current relation */
  relation: Pick<Association["relation"], "iri" | "name" | "inverse">;
  /** whether to display arrows vertically */
  vertical?: boolean;
}

const props = defineProps<Props>();

/** direction of arrows */
const arrowDirection = computed(() => {
  if (props.vertical) {
    if (props.relation.inverse) return "up";
    else return "down";
  } else {
    if (props.relation.inverse) return "left";
    else return "right";
  }
});
</script>

<style lang="scss" scoped>
.relation {
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
