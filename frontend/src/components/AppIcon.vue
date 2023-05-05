<!--
  wrapper for font awesome icon or custom icon loaded inline
-->

<template>
  <FontAwesomeIcon
    v-if="_icon?.type === 'fa'"
    :icon="_icon?.definition"
    :data-icon="icon"
    aria-hidden="true"
  />
  <InlineSvg
    v-else-if="_icon?.type === 'custom'"
    :src="_icon?.src"
    class="icon"
    :data-icon="icon"
    aria-hidden="true"
  />
  <svg
    v-else-if="_icon?.type === 'initials'"
    viewBox="-10 -10 120 120"
    class="initials"
  >
    <circle cx="50" cy="50" r="55" />
    <text x="50" y="54">
      {{ _icon?.letters }}
    </text>
  </svg>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import InlineSvg from "vue-inline-svg";
import type {
  IconDefinition,
  IconName,
  IconPrefix,
} from "@fortawesome/fontawesome-svg-core";
import { findIconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

type Props = {
  /**
   * kebab-case name of icon to show. for font awesome, without fas/far/etc
   * prefix. for custom icon, match filename, without extension.
   */
  icon?: string;
};

const props = defineProps<Props>();

type _Icon =
  | { type: "fa"; definition: IconDefinition }
  | { type: "custom"; src: string }
  | { type: "initials"; letters: string };

/** computed icon */
const _icon = ref<_Icon>();

watch(
  () => props.icon,
  async () => {
    /** first look for font awesome icon with matching name */
    for (const prefix of ["fas", "far", "fab"]) {
      const match = findIconDefinition({
        prefix: prefix as IconPrefix,
        iconName: props.icon as IconName,
      });
      if (match) {
        _icon.value = { type: "fa", definition: match };
        return;
      }
    }

    /** otherwise, look for custom icon with matching name */
    try {
      const src = (await import(`../assets/icons/${props.icon}.svg`)).default;
      _icon.value = { type: "custom", src };
      return;
    } catch (error) {
      console.error("couldn't load custom icon", error);
    }

    /** last resort, use initials */
    _icon.value = {
      type: "initials",
      letters:
        props.icon
          ?.replace(/^category-/, "")
          .split("-")
          .map((word) => (word[0] || "").toUpperCase())
          .join("") || "",
    };
  },
  { immediate: true }
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
