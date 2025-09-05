<template>
  <component
    :is="component"
    ref="button"
    :class="['button', design, color, { text }]"
    :to="to"
    :type="type"
    @click="copy ? copyToClipboard(text) : click"
  >
    <AppIcon v-if="icon && iconPosition === 'left'" :icon="icon" class="icon" />
    <span v-if="text" class="truncate">{{ text }}</span>
    <!-- icon on the RIGHT (default) -->
    <AppIcon
      v-if="icon && iconPosition === 'right'"
      :icon="icon"
      class="icon"
    />
    <!-- optional info icon -->
    <AppIcon
      v-if="info"
      v-tooltip="infoTooltip"
      icon="info-circle"
      class="info-icon"
    />
  </component>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { copyToClipboard } from "@/util/string";

type Props = {
  /** text to show */
  text?: string;
  /** icon to show */
  icon?: string;
  /** where to place the icon relative to text */
  iconPosition?: "left" | "right";
  /** location to link to */
  to?: string;
  /** on click action */
  click?: () => unknown;
  /** visual design */
  design?: "normal" | "circle" | "small" | "tile" | "big" | "link";
  /** color */
  color?: "primary" | "secondary" | "none";
  /** whether to copy text prop to clipboard on click */
  copy?: boolean;
  /** html button type attribute */
  type?: string;
  /** show an “i” info icon on the right */
  info?: boolean;
  /** tooltip text for the info icon */
  infoTooltip?: string;
};

const props = withDefaults(defineProps<Props>(), {
  text: "",
  icon: "",
  iconPosition: "right",
  to: "",
  click: undefined,
  design: "normal",
  color: "primary",
  copy: false,
  type: "button",
  info: false,
  infoTooltip: "",
});

/** element ref */
const button = ref<HTMLButtonElement>();

/** type of component to render */
const component = computed(() => (props.to ? "AppLink" : "button"));

/** allow parent to access ref */
defineExpose({ button });
</script>

<style lang="scss" scoped>
.button {
  display: inline-flex;
  appearance: none;
  flex-grow: 0;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  max-width: 100%;
  gap: 10px;
  text-decoration: none;
  transition:
    color $fast,
    background $fast,
    opacity $fast,
    box-shadow $fast;

  &.button-base {
    min-height: 40px;
    padding: 5px 20px;
    border-radius: $rounded;
    color: $off-black;
    font-weight: 500;
    font-size: 1rem;

    &.primary {
      background: $theme-light;
    }
    &.secondary {
      background: $light-gray;
    }

    &:hover,
    &:focus {
      outline: none;
      box-shadow: $outline;
    }
  }

  &.normal {
    @extend .button-base;
    min-width: min(200px, calc(100% - 40px));
  }

  &.tile {
    @extend .button-base;
    width: fit-content;
  }

  &.big {
    min-width: min(300px, 100% - 40px);
    padding: 0px 30px;
    font-size: 1.75rem;
  }

  &.circle {
    border-radius: 999px;
    color: $off-black;

    &.text {
      min-width: 2em;
      min-height: 2em;
      padding: 0.25em 0.75em;
    }
    &:not(.text) {
      width: 2.5em;
      height: 2.5em;
    }

    &.primary {
      background: $theme-light;
    }
    &.secondary {
      background: $light-gray;
    }

    &:hover,
    &:focus {
      outline: none;
      box-shadow: $outline;
    }
  }

  &.small {
    padding: 3px;
    border-radius: $rounded;

    &.primary {
      color: $theme;
    }
    &.secondary {
      color: $off-black;
    }
    &:hover,
    &:focus {
      color: $black;
    }
  }

  &.tile {
    width: fit-content;
    min-height: 40px;
    padding: 5px 20px;
    border-radius: $rounded;
    color: $off-black;
    font-weight: 500;
    font-size: 1rem;

    &.primary {
      background: $theme-light;
    }
    &.secondary {
      background: $light-gray;
    }

    &:hover,
    &:focus {
      outline: none;
      box-shadow: $outline;
    }
  }

  /* link-style button*/
  &.link {
    min-height: unset;
    padding: 0;
    gap: 6px;
    background: transparent;
    color: $theme;
    text-decoration: none;

    &:hover .truncate,
    &:focus .truncate {
      text-decoration: underline;
      text-decoration-thickness: 2px;
      text-underline-offset: 3px;
    }

    .truncate {
      text-decoration: underline;
      text-decoration-thickness: 1px;
      text-underline-offset: 3px;
    }

    &:focus {
      border-radius: 6px;
      outline: none;
      box-shadow: 0 0 0 3px rgba($theme, 0.25);
    }
  }
}

.fill {
  .button.circle.primary {
    background: $theme-mid;
  }
}

.icon {
  margin-left: 0.5em;
}

/* When icon is on the LEFT, remove the left margin and add a right one */
.button.link .icon,
.button.normal .icon,
.button.small .icon,
.button.tile .icon,
.button.big .icon {
  margin-left: 0.5em;
}
.button.link.icon-left .icon {
  margin-right: 0.25em;
  margin-left: 0;
}

.info-icon {
  margin-left: 0.5em;
}
</style>
