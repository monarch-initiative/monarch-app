<!--
  looks like a button and either does something (<button>) or goes somewhere (<a>)
-->

<template>
  <component
    :is="component"
    ref="button"
    class="button"
    :to="to"
    :type="type"
    :data-design="design"
    :data-color="color"
    :data-text="!!text"
    @click="copy ? copyToClipboard() : click"
  >
    <span v-if="text" class="truncate">{{ text }}</span>
    <AppIcon v-if="icon" :icon="icon" />
  </component>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { snackbar } from "./TheSnackbar.vue";

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
async function copyToClipboard() {
  await window.navigator.clipboard.writeText(props.text || "");
  snackbar("Text copied");
}

/** type of component to render */
const component = computed(() => (props.to ? "AppLink" : "button"));

/** allow parent to access ref */
defineExpose({ button });
</script>

<style lang="scss" scoped>
.button {
  appearance: none;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  max-width: 100%;
  gap: 10px;
  flex-grow: 0;
  flex-shrink: 0;
  text-decoration: none;
  transition: color $fast, background $fast, opacity $fast, box-shadow $fast;

  &[data-design="normal"] {
    min-width: min(200px, calc(100% - 40px));
    min-height: 40px;
    padding: 5px 20px;
    color: $off-black;
    border-radius: $rounded;
    font-size: 1rem;
    font-weight: 500;

    &[data-color="primary"] {
      background: $theme-light;
    }

    &[data-color="secondary"] {
      background: $light-gray;
    }

    &:hover,
    &:focus {
      outline: none;
      box-shadow: $outline;
    }
  }

  &[data-design="circle"] {
    color: $off-black;
    border-radius: 999px;

    &[data-text="true"] {
      min-width: 2em;
      min-height: 2em;
      padding: 0.25em 0.75em;
    }

    &:not([data-text="true"]) {
      width: 2.5em;
      height: 2.5em;
    }

    &[data-color="primary"] {
      background: $theme-light;
    }

    &[data-color="secondary"] {
      background: $light-gray;
    }

    &:hover,
    &:focus {
      outline: none;
      box-shadow: $outline;
    }
  }

  &[data-design="small"] {
    flex-direction: row-reverse;
    padding: 3px;
    border-radius: $rounded;

    &[data-color="primary"] {
      color: $theme;
    }

    &[data-color="secondary"] {
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
[data-design="fill"] {
  .button[data-design="circle"][data-color="primary"] {
    background: $theme-mid;
  }
}
</style>
