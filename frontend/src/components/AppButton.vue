<!--
  looks like a button and either does something (<button>) or goes somewhere (<a>)
-->

<template>
  <component
    :is="component"
    ref="button"
    :class="['button', design, color, { text }]"
    :to="to"
    :type="type"
    @click="copy ? copyFunc() : click"
  >
    <span v-if="text" class="truncate">{{ text }}</span>
    <AppIcon v-if="icon" :icon="icon" />
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
  /** location to link to */
  to?: string;
  /** on click action */
  click?: () => unknown;
  /** visual design */
  design?: "normal" | "circle" | "small";
  /** color */
  color?: "primary" | "secondary" | "none";
  /** whether to copy text prop to clipboard on click */
  copy?: boolean;
  /** html button type attribute */
  type?: string;
};

const props = withDefaults(defineProps<Props>(), {
  text: "",
  icon: "",
  to: "",
  click: undefined,
  design: "normal",
  color: "primary",
  copy: false,
  type: "button",
});

/** element ref */
const button = ref();

/** copy text prop to clipboard */
async function copyFunc() {
  copyToClipboard(props.text);
}

/** type of component to render */
const component = computed(() => (props.to ? "AppLink" : "button"));

/** allow parent to access ref */
defineExpose({ button });
</script>

<style lang="scss" scoped>
.button {
  display: inline-flex;
  flex-grow: 0;
  flex-shrink: 0;
  justify-content: center;
  align-items: center;
  gap: 10px;
  appearance: none;
  transition:
    color $fast,
    background $fast,
    opacity $fast,
    box-shadow $fast;
  max-width: 100%;
  text-decoration: none;

  &.normal {
    border-radius: $rounded;
    padding: 5px 20px;
    min-width: min(200px, calc(100% - 40px));
    min-height: 40px;
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

  &.circle {
    border-radius: 999px;
    color: $off-black;

    &.text {
      padding: 0.25em 0.75em;
      min-width: 2em;
      min-height: 2em;
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
    flex-direction: row-reverse;
    border-radius: $rounded;
    padding: 3px;

    &.primary {
      color: $theme;
    }

    &.secondary {
      color: $dark-gray;
    }

    &:hover,
    &:focus {
      color: $black;
    }
  }
}
</style>

<style lang="scss">
.fill {
  .button.circle.primary {
    background: $theme-mid;
  }
}
</style>
