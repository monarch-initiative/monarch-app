<!--
  grid container for multiple AppDetail components
-->

<template>
  <div class="details" :style="{ '--gap': gap || '30px' }">
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  gap?: string;
}>();
</script>

<style lang="scss" scoped>
.details {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  width: 100%;
  gap: var(--gap);
}
</style>
