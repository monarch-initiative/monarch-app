<!-- 
  utility component to conveniently and consistently align and space items.
  use only for basic flex needs. for anything more (like media queries), use 
  in-situ css.
-->

<template>
  <div
    ref="element"
    :class="['flex', flow, direction, gap]"
    :style="{ justifyContent, alignItems }"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

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
  alignH?: "left" | "center" | "right" | "stretch";
  /** vertical alignment */
  alignV?: "top" | "center" | "bottom" | "stretch";
};

const props = withDefaults(defineProps<Props>(), {
  flow: "block",
  direction: "row",
  gap: "medium",
  alignH: "center",
  alignV: "center",
});

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

/** css flex props */
const justifyContent = computed(() =>
  props.direction === "col" ? alignMap[props.alignV] : alignMap[props.alignH],
);
const alignItems = computed(() =>
  props.direction === "col" ? alignMap[props.alignH] : alignMap[props.alignV],
);

const element = ref();

defineExpose({ element });
</script>

<style lang="scss" scoped>
.flex {
  &.block {
    display: flex;
    width: 100%;
  }

  &.inline {
    display: inline-flex;
  }

  &.row {
    flex-wrap: wrap;
  }

  &.col {
    flex-direction: column;
  }

  &.none {
    gap: 0;
  }

  &.tiny {
    gap: 5px;
  }

  &.small {
    gap: 10px;
  }

  &.medium {
    gap: 20px;
  }

  &.big {
    gap: 40px;
  }
}
</style>
