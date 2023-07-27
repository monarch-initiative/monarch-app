<!--
  wrapper for font awesome icon or custom icon loaded inline
-->

<template>
  <component
    :is="customIcon"
    v-if="isCustom"
    class="icon"
    :data-icon="icon"
    aria-hidden="true"
  />
  <FontAwesomeIcon
    v-else-if="fontAwesome"
    :icon="fontAwesome"
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
import { computed, defineAsyncComponent, ref } from "vue";
import { kebabCase } from "lodash";
import type { IconName, IconPrefix } from "@fortawesome/fontawesome-svg-core";
import { findIconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

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
    const result = await import(`../assets/icons/${kebabCase(props.icon)}.svg`);
    console.log(props.icon, result.render());
    return result;
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
      .join("") || "",
);
</script>

<style lang="scss" scoped>
.icon {
  height: 1em;
}

/** category icon styles */
[data-icon^="category-"] {
  fill: none;
  stroke: currentColor;
  stroke-width: 5;
  stroke-linecap: round;
  stroke-linejoin: round;
  height: 1.2em;
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
    text-anchor: middle;
    dominant-baseline: middle;
    font-size: 50px;
  }
}
</style>
