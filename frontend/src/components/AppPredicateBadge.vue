<!--
  an icon, text, and link for a predicate between nodes in the knowledge graph
-->

<template>
  <span class="predicate">
    <AppIcon v-if="arrows" class="arrow" :icon="`arrow-${arrowDirection}`" />
    <span v-if="association.negated" class="negated-text">NOT</span>

    <span
      class="predicate-label"
      :class="{ 'highlighted-text': highlight }"
      v-html="getFormattedPredicateLabel(predicate)"
    /><AppPredicateInfo
      v-if="predicateString"
      :predicate="predicateString"
      class="predicate-info-icon"
    />

    <AppIcon v-if="arrows" class="arrow" :icon="`arrow-${arrowDirection}`" />
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { type DirectionalAssociation } from "@/api/model";
import AppPredicateInfo from "@/components/AppPredicateInfo.vue";

type Props = {
  /** current association */
  association: Partial<DirectionalAssociation>;
  /** whether to reverse the direction of arrows */
  reverse?: boolean;
  /** whether to display arrows vertically */
  vertical?: boolean;
  arrows?: boolean;
  /** boolean to use for hightlighting */
  highlight?: boolean;
};

const props = defineProps<Props>();

const predicate = computed(
  () =>
    props?.association?.highlighting?.predicate?.[0] ??
    props.association.predicate,
);

/** single predicate value for the explainer */
const predicateString = computed(() => {
  const value = predicate.value;
  return (Array.isArray(value) ? value[0] : value) ?? "";
});
const getFormattedPredicateLabel = (category?: string | string[]) => {
  const raw = Array.isArray(category) ? category[0] : category;
  if (!raw) return "";

  const value = raw.replace(/^biolink:/, "").replace(/_/g, " ");
  return value;
};

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
  }
}

/* only the label wraps; the info icon stays attached to it (no orphan icon
   on a new line in constrained columns) */
.predicate-label {
  overflow-wrap: anywhere;
}

.predicate-info-icon {
  white-space: nowrap;
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
.negated-text {
  color: $error;
  font-weight: 600;
}

.highlighted-text ::v-deep(em) {
  background-color: yellow;
}
</style>
