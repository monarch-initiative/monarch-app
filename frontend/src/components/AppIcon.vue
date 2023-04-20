<!--
  wrapper for font awesome icon or custom icon loaded inline
-->

<template>
  <InlineSvg
    v-if="custom"
    :src="custom"
    class="icon"
    aria-hidden="true"
    :data-icon="icon"
  />
  <FontAwesomeIcon
    v-else-if="fa"
    :icon="fa"
    :data-icon="icon"
    aria-hidden="true"
  />
  <svg v-else-if="initials" viewBox="-10 -10 120 120" class="initials">
    <circle cx="50" cy="50" r="55" />
    <text x="50" y="54">
      {{ initials }}
    </text>
  </svg>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import InlineSvg from "vue-inline-svg";
import type { IconName, IconPrefix } from "@fortawesome/fontawesome-svg-core";
import { findIconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

type Props = {
  /**
   * Kebab-case name of icon to show. for font awesome, without fas/far/etc
   * prefix. for custom icon, match filename, without extension.
   */
  icon?: string;
};

const props = defineProps<Props>();

/** Find custom icon with matching name, if there is one */
const custom = ref("");
watch(
  () => props.icon,
  async () => {
    try {
      custom.value = (await import(`../assets/icons/${props.icon}.svg`)).default;
    } catch (error) {}
  },
  { immediate: true }
);

/** Find font awesome icon with matching name, if there is one */
const fa = computed(() => {
  for (const prefix of ["fas", "far", "fab"]) {
    const match = findIconDefinition({
      prefix: prefix as IconPrefix,
      iconName: props.icon as IconName,
    });
    if (match) return match;
  }

  return null;
});

/** Initials as fallback */
const initials = computed(() =>
  props.icon
    ?.replace(/^category-/, "")
    .split("-")
    .map((word) => (word[0] || "").toUpperCase())
    .join("")
);
</script>

<style lang="scss" scoped>
.icon {
  height: 1em;
}

/** common category icon styles */
[data-icon^="category-"] {
  height: 1.2em;
  fill: none;
  stroke: currentColor;
  stroke-width: 5;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.initials {
  height: 1.2em;

  circle {
    fill: none;
    stroke: currentColor;
    stroke-width: 5;
  }

  text {
    fill: currentColor;
    font-size: 50px;
    text-anchor: middle;
    dominant-baseline: middle;
  }
}
</style>
