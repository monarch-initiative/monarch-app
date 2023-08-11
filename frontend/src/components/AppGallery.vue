<!-- 
  responsive grid of arbitrary content items
-->

<template>
  <div class="gallery" :data-size="size">
    <slot />
  </div>
</template>

<script setup lang="ts">
type Props = {
  /** size of items in gallery */
  size?: "small" | "medium" | "big";
};

withDefaults(defineProps<Props>(), { size: "medium" });

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();
</script>

<style lang="scss" scoped>
$tablet: 900px;
$phone: 600px;
$col: minmax(0, 1fr);

.gallery {
  display: grid;
  justify-items: stretch;
  width: 100%;

  &[data-size="small"] {
    grid-template-columns: $col $col $col $col $col;
    gap: 20px;

    @media (max-width: $tablet) {
      grid-template-columns: $col $col $col;
    }

    @media (max-width: $phone) {
      grid-template-columns: $col $col;
    }
  }

  &[data-size="medium"] {
    grid-template-columns: $col $col $col;
    gap: 40px;

    @media (max-width: $tablet) {
      grid-template-columns: $col $col;
    }

    @media (max-width: $phone) {
      grid-template-columns: $col;
    }
  }

  &[data-size="big"] {
    grid-template-columns: $col $col;
    gap: 40px;

    @media (max-width: $phone) {
      grid-template-columns: $col;
    }
  }
}
</style>

<style lang="scss">
/** force no margins for children since grid already provides gap */
.gallery > :deep(*) {
  margin: 0 !important;
}
</style>
