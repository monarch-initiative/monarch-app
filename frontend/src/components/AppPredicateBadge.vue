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
      v-if="predicateString && explain"
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
  /**
   * Whether to offer the definition popover. Views that already spell the
   * definition out set this false: a second route to the same text is noise,
   * and those views are modals, where a popover would have to out-stack the
   * modal to be usable at all.
   */
  explain?: boolean;
  /** boolean to use for hightlighting */
  highlight?: boolean;
};

const props = withDefaults(defineProps<Props>(), { explain: true });

const predicate = computed(
  () =>
    props?.association?.highlighting?.predicate?.[0] ??
    props.association.predicate,
);

/**
 * Single predicate value for the explainer.
 *
 * Deliberately not `predicate`, which prefers the search highlight: Solr wraps
 * matches in markup, so a row matching a search returns
 * `biolink:applied_to_<em>treat</em>`. That is right for the label, which
 * renders as HTML, but as an identifier it finds nothing in the biolink model
 * and leaks tags into the button's accessible name and the modal's title.
 * Highlighting is for display only.
 */
const predicateString = computed(() => {
  const value = props.association.predicate;
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
