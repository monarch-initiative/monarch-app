<!--
  wrapper for font awesome icon or custom icon loaded inline
-->

<template>
  <component
    :is="customIcon"
    v-if="isCustom"
    class="custom"
    :style="{ '--thickness': thickness }"
    :data-icon="icon"
    aria-hidden="true"
  />
  <FontAwesomeIcon
    v-else-if="fontAwesome"
    :icon="fontAwesome"
    class="fa"
    :style="{ '--thickness': thickness }"
    aria-hidden="true"
  />
  <svg
    v-else-if="initials"
    viewBox="-10 -10 120 120"
    class="initials"
    :style="{ '--thickness': thickness }"
  >
    <circle fill="none" stroke="currentColor" cx="50" cy="50" r="55" />
    <text x="50" y="54">
      {{ initials }}
    </text>
  </svg>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, ref } from "vue";
import { kebabCase } from "lodash";
import type { IconName, IconPrefix } from "@fortawesome/fontawesome-svg-core";
import { findIconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { useElementSize } from "@vueuse/core";

type Props = {
  /**
   * kebab-case name of icon to show. for font awesome, without fas/far/etc
   * prefix. for custom icon, match filename, without extension.
   */
  icon: string;
};

const props = defineProps<Props>();

/** look for font awesome icon with matching name */
const fontAwesome = computed(() => {
  for (const prefix of ["fas", "far", "fab"]) {
    const match = findIconDefinition({
      prefix: prefix as IconPrefix,
      iconName: props.icon as IconName,
    });
    if (match) return match;
  }
  return null;
});

const isCustom = ref(true);

/** look for custom icon with matching name */
const customIcon = defineAsyncComponent(async () => {
  try {
    return await import(`../assets/icons/${kebabCase(props.icon)}.svg`);
  } catch {
    isCustom.value = false;
    return await import(`../assets/icons/loading.svg`);
  }
});

/** initials */
const initials = computed(
  () =>
    props.icon
      ?.replace(/^category-/, "")
      .split("-")
      .map((word) => (word[0] || "").toUpperCase())
      .slice(0, 2)
      .join("") || "",
);

/** dynamic line thickness */
const thickness = computed(() => {
  /** leave opportunity for thickness based on absolute size in the future */
  return 5;
});
</script>

<style lang="scss" scoped>
.custom {
  height: 1em;

  /** resource icon styles */
  &[data-icon^="resource-"] {
    filter: brightness(0.2);
  }

  /** category icon styles */
  &[data-icon^="category-"],
  &[data-icon^="association-"] {
    fill: none;
    stroke: currentColor;
    stroke-width: var(--thickness);
    stroke-linecap: round;
    stroke-linejoin: round;
  }
}

.initials {
  height: 1em;

  circle {
    fill: none;
    stroke: currentColor;
    stroke-width: var(--thickness);
  }

  text {
    fill: currentColor;
    text-anchor: middle;
    dominant-baseline: middle;
    font-size: 50px;
  }
}
</style>
