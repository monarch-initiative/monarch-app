<!--
  wrapper for font awesome icon or custom icon loaded inline
-->

<template>
  <component
    :is="customIcon"
    v-if="isCustom"
    :class="['app-icon', type]"
    aria-hidden="true"
    @vue:updated="({ el }: VNode) => customMounted(el, true)"
    v-tooltip="props.tooltip"
  />
  <FontAwesomeIcon
    v-else-if="fontAwesome"
    :icon="fontAwesome"
    class="app-icon"
    aria-hidden="true"
    :style="props.size ? { fontSize: props.size } : undefined"
  />
  <img
    v-else-if="isPng"
    :src="`/icons/${props.icon}`"
    :alt="props.icon"
    class="app-icon img"
    aria-hidden="true"
    v-tooltip="props.tooltip"
  />
  <svg
    v-else-if="initials"
    v-tooltip="props.tooltip"
    viewBox="0 0 100 100"
    class="app-icon initials"
    @vue:mounted="({ el }: VNode) => customMounted(el)"
  >
    <circle class="outline" cx="50" cy="50" r="50" />
    <text x="50" y="54">
      {{ initials }}
    </text>
  </svg>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, ref, type VNode } from "vue";
import { kebabCase } from "lodash";
import type { IconName, IconPrefix } from "@fortawesome/fontawesome-svg-core";
import { findIconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { getCategoryColor } from "@/api/categories";

type Props = {
  /**
   * kebab-case name of icon to show. for font awesome, without fas/far/etc
   * prefix. for custom icon, match filename, without extension.
   */
  icon: string;
  size?: string;
  tooltip?: string;
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
const isPng = computed(() => props.icon.endsWith(".png"));

/** look for custom icon with matching name */
const customIcon = defineAsyncComponent(async () => {
  if (isPng.value) {
    isCustom.value = false;
    return;
  }
  try {
    return await import(`../assets/icons/${kebabCase(props.icon)}.svg`);
  } catch {
    isCustom.value = false;
    return await import(`../assets/icons/loading.svg`);
  }
});

/** special icon type based on name prefix */
const type = computed(() => {
  if (props.icon.startsWith("category-")) return "category";
  if (props.icon.startsWith("resource-")) return "resource";
  return "";
});

/** initials */
const initials = computed(
  () =>
    props.icon
      ?.replace(new RegExp(`^${type.value}-`), "")
      .split("-")
      .map((word) => (word[0] || "").toUpperCase())
      .slice(0, 2)
      .join("") || "",
);

/** when custom icon mounted */
function customMounted(element: VNode["el"], createCircle = false) {
  /** add child elements to category icon */
  if (
    element &&
    element instanceof SVGSVGElement &&
    type.value === "category"
  ) {
    /** set color for category */
    element.style.setProperty("--color", getCategoryColor(props.icon));

    if (createCircle) {
      /** create circle outline */
      const outline = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "circle",
      );
      outline.setAttribute("cx", "50");
      outline.setAttribute("cy", "50");
      outline.setAttribute("r", "50");
      outline.classList.add("outline");
      element.insertBefore(outline, element.firstChild!);
    }
  }
}
</script>

<style lang="scss" scoped>
.app-icon {
  height: 1em;
}
.app-icon.img {
  width: auto;
  object-fit: contain;
}
.category {
  fill: none;
  stroke: $white;
  stroke-width: 5;
  stroke-linecap: round;
  stroke-linejoin: round;
}

:deep(.outline) {
  stroke: none;
  fill: var(--color, currentColor);
  transform: scale(1.1);
  transform-box: fill-box;
  transform-origin: center;
}

.initials {
  text {
    fill: $white;
    text-anchor: middle;
    dominant-baseline: middle;
    font-size: 50px;
  }
}

.resource {
  filter: brightness(0.2);
}
</style>
