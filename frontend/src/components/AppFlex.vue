<!-- 
  utility component to conveniently and consistently align and space items.
  use only for basic flex needs. for anything more (like media queries), use 
  in-situ css.
-->

<template>
  <div
    class="flex"
    :data-flow="flow"
    :data-direction="direction"
    :data-gap="gap"
    :style="{ justifyContent, alignItems }"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

/** map nice human align names to css flex align names */
const alignMap = {
  left: "flex-start",
  top: "flex-start",
  center: "center",
  right: "flex-end",
  bottom: "flex-end",
  stretch: "stretch",
};

type Props = {
  /** flex display (whether container takes up full width) */
  flow?: "inline" | "block";
  /** horizontal or vertical */
  direction?: "row" | "col";
  /** spacing between items */
  gap?: "none" | "tiny" | "small" | "medium" | "big";
  /** horizontal alignment */
  hAlign?: "left" | "center" | "right" | "stretch";
  /** vertical alignment */
  vAlign?: "top" | "center" | "bottom" | "stretch";
}

const props = withDefaults(defineProps<Props>(), {
  flow: "block",
  direction: "row",
  gap: "medium",
  hAlign: "center",
  vAlign: "center",
});

/** css flex props */
const justifyContent = computed(() =>
  props.direction === "col" ? alignMap[props.vAlign] : alignMap[props.hAlign]
);
const alignItems = computed(() =>
  props.direction === "col" ? alignMap[props.hAlign] : alignMap[props.vAlign]
);
</script>

<style lang="scss" scoped>
.flex {
  &[data-flow="block"] {
    display: flex;
    width: 100%;
  }

  &[data-flow="inline"] {
    display: inline-flex;
  }

  &[data-direction="row"] {
    flex-wrap: wrap;
  }

  &[data-direction="col"] {
    flex-direction: column;
  }

  &[data-gap="none"] {
    gap: 0;
  }

  &[data-gap="tiny"] {
    gap: 5px;
  }

  &[data-gap="small"] {
    gap: 10px;
  }

  &[data-gap="medium"] {
    gap: 20px;
  }

  &[data-gap="big"] {
    gap: 40px;
  }
}
</style>
