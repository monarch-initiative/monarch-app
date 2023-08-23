<!--
  heading component with anchor link and (optionally) automatic level
-->

<template>
  <component :is="tag || 'div'" :id="link" ref="heading">
    <!-- heading icon -->
    <AppIcon v-if="icon" :icon="icon" :fallback="fallbackIcon" class="icon" />

    <!-- heading content -->
    <slot />

    <!-- heading anchor -->
    <AppLink
      v-if="link"
      :to="'#' + link"
      class="anchor"
      :aria-label="'Link to this section'"
    >
      <AppIcon icon="link" />
    </AppLink>
  </component>
</template>

<script setup lang="ts">
import { onMounted, onUpdated, ref } from "vue";
import { kebabCase } from "lodash";

type Props = {
  /** manually specified heading id */
  id?: string;
  /** manually specified heading level */
  level?: number;
  /** icon to show next to text */
  icon?: string;
  /** fall back icon */
  fallbackIcon?: string;
};

const props = defineProps<Props>();

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

/** tag of heading (default to blank to avoid conflict with automatic level) */
const tag = ref("");
/** hash link of heading */
const link = ref("");

/** heading ref */
const heading = ref<HTMLElement>();

/** get heading level/tag, i.e. h1, h2, h3, etc */
function getTag() {
  /** if level manually specified, just use that */
  if (props.level) return "h" + props.level;

  /**
   * otherwise, determine automatically based on heading's position in document
   * https://dequeuniversity.com/rules/axe/4.1/page-has-heading-one
   */

  /** heading element */
  const element = heading.value;
  /** section element */
  const parent = element?.parentElement;

  /** if heading is first in section */
  const firstHeading = element?.matches("*:first-child");
  /** if section is first in main */
  const firstSection = parent?.matches("*:first-child");

  /** determine level */
  if (firstSection) {
    if (firstHeading) return "h1";
    else return "h2";
  } else {
    if (firstHeading) return "h2";
    else return "h3";
  }
}

/** determine link from text content of heading */
function getLink() {
  /**
   * per accessibility conventions, h1's should only appear once and near top of
   * doc. thus, anchors aren't useful for them.
   */
  if (tag.value === "h1") return "";
  else return kebabCase(props.id || heading.value?.textContent || "");
}

/** update tag and link on mount and change */
function update() {
  tag.value = getTag();
  link.value = getLink();
}
onMounted(update);
onUpdated(update);
</script>

<style lang="scss" scoped>
.anchor {
  display: inline-block;
  width: 0;
  margin-left: 0.75em;
  font-size: 0.8em;
  text-decoration: none;
  opacity: 0;
  transition:
    opacity $fast,
    color $fast;
}

.anchor:focus {
  opacity: 1;
}

.icon {
  position: relative;
  top: -1px;
  margin-right: 0.75em;
  color: $gray;
  vertical-align: middle;
}

h1,
h2,
h3 {
  &:hover .anchor {
    opacity: 1;
  }
}
</style>

<style lang="scss">
[data-design="fill"] {
  h1,
  h2,
  h3 {
    .icon {
      height: 1.2em;
      color: $theme;
    }
  }
}
</style>
