<!-- 
  responsive grid of arbitrary content items
-->

<template>
  <div
    :class="['gallery', `cols-${cols}`]"
    :style="{ '--max-cols': cols, '--content-cols': Math.min(cells, cols) }"
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
$tablet: 900px;
$phone: 600px;

.gallery {
  --gap: 40px;
  // intended number of cols per row, limited by screen size col reduction
  --intended-cols: min(var(--max-cols), var(--screen-cols));
  // actual number of cols with content, limited by screen size col reduction
  --actual-cols: min(var(--content-cols), var(--screen-cols));
  // size of cell if row was full
  --cell: (100% - (var(--intended-cols) - 1) * var(--gap)) /
    var(--intended-cols);
  display: grid;
  grid-template-columns: repeat(var(--actual-cols), minmax(0, 1fr));
  grid-auto-rows: 1fr;
  place-content: center;
  gap: var(--gap);
  // when content doesn't fill first row, limit width of gallery so that cell size is same as if first row was full
  // e.g. on team page, so portraits in groups with only 1-2 members aren't bigger than portraits in groups with 3+ members
  max-width: calc(
    (var(--cell)) * var(--content-cols) + (var(--content-cols) - 1) * var(--gap)
  );

  @media (min-width: 0) {
    --screen-cols: 1;
  }

  @media (min-width: $phone) {
    --screen-cols: 2;
  }

  @media (min-width: $tablet) {
    --screen-cols: var(--max-cols) !important;
  }

  &.cols-4,
  &.cols-5 {
    --gap: 20px;

    @media (min-width: 0) {
      --screen-cols: 2;
    }

    @media (min-width: $phone) {
      --screen-cols: 3;
    }
  }
}
</style>

<style lang="scss">
.gallery > * {
  /** force no margins for children since grid already provides gap */
  margin: 0 !important;
}
</style>
