<!--
  checkbox with arbitrary content (slot) and icon
-->

<template>
  <aside v-if="open" class="banner">
    <div>
      <slot />
    </div>
    <AppButton icon="xmark" text="Close" design="small" @click="open = false" />
  </aside>
</template>

<script setup lang="ts">
import { ref } from "vue";

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

const open = ref(true);
</script>

<style lang="scss" scoped>
.banner {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  padding: 20px;
  gap: 20px;
  background: $theme-light;
  text-align: center;
}
</style>
