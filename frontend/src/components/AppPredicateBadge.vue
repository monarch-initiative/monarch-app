<!--
  an icon, text, and link for a predicate between nodes in the knowledge graph
-->

<template>
  <span class="predicate">
    <AppIcon class="arrow" :icon="`arrow-${arrowDirection}`" />
    {{ startCase(getCategoryLabel(association.predicate)).toLowerCase() }}
    <AppIcon class="arrow" :icon="`arrow-${arrowDirection}`" />
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { startCase } from "lodash";
import { getCategoryLabel } from "@/api/categories";
import {
  AssociationDirectionEnum,
  type DirectionalAssociation,
} from "@/api/model";

type Props = {
  /** current association */
  association: Partial<DirectionalAssociation>;
  /** whether to display arrows vertically */
  vertical?: boolean;
};

const props = defineProps<Props>();

/** direction of arrows */
const arrowDirection = computed(() =>
  props.association.direction === AssociationDirectionEnum.incoming
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
