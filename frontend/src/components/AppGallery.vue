<!-- 
  responsive grid of arbitrary content items
-->

<template>
  <div
    :class="['gallery', `cols-${cols}`]"
    :style="{ '--max-cols': cols, '--cells': Math.min(cells, cols) }"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed, type VNode } from "vue";

type Props = {
  /** max number of columns */
  cols?: number;
};

withDefaults(defineProps<Props>(), { cols: 3 });

type Slots = {
  default: () => VNode[];
};

const slots = defineSlots<Slots>();

/** number of child elements (cells) in slot */
const cells = computed(
  () =>
    Object.values(slots.default()[0]?.children || []).length ||
    slots.default().length,
);
</script>

<style lang="scss" scoped>
.gallery {
  --gap: 40px;
  display: grid;
  grid-template-columns: repeat(min(var(--cells), var(--cols)), minmax(0, 1fr));
  place-content: center;
  max-width: calc(
    (
        (100% - (min(var(--max-cols), var(--cols)) - 1) * var(--gap)) /
          min(var(--max-cols), var(--cols))
      ) * var(--cells) + (var(--cells) - 1) * var(--gap)
  );
  gap: var(--gap);

  @media (min-width: 0) {
    --cols: 1;

    &.cols-4,
    &.cols-5 {
      --cols: 2;
    }
  }

  @media (min-width: 600px) {
    --cols: 2;

    &.cols-4,
    &.cols-5 {
      --cols: 3;
    }
  }

  @media (min-width: 900px) {
    --cols: var(--max-cols) !important;
  }

  &.cols-4,
  &.cols-5 {
    --gap: 20px;
  }
}
</style>

<style lang="scss">
.gallery > * {
  /** force no margins for children since grid already provides gap */
  margin: 0 !important;
}
</style>
