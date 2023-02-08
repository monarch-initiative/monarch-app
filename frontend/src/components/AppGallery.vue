<!-- 
  responsive grid of arbitrary content items
-->

<template>
  <div class="gallery" :data-size="size">
    <slot />
  </div>
</template>

<script setup lang="ts">
interface Props {
  /** size of items in gallery */
  size?: "small" | "medium" | "big";
}

withDefaults(defineProps<Props>(), { size: "medium" });
</script>

<style lang="scss" scoped>
$two: 900px;
$one: 600px;
$cell: minmax(100px, 1fr);

.gallery {
  display: grid;
  grid-template-columns: $cell $cell $cell;
  justify-items: stretch;

  &[data-size="small"] {
    gap: 20px;
  }

  &[data-size="medium"] {
    gap: 40px;
  }

  &[data-size="big"] {
    gap: 40px;
    grid-template-columns: $cell $cell;

    @media (max-width: $one) {
      grid-template-columns: $cell;
    }
  }

  @media (max-width: $two) {
    grid-template-columns: $cell $cell;
  }

  @media (max-width: $one) {
    grid-template-columns: $cell;
  }
}
</style>

<style lang="scss">
/** force no margins for children since grid already provides gap */
.gallery > :deep(*) {
  margin: 0 !important;
}
</style>
