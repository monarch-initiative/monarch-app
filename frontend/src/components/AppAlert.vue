<!--
  simple alert box
-->

<template>
  <div class="alert">
    <AppIcon :icon="icon" class="icon" />
    <slot />
  </div>
</template>

<script setup lang="ts">
type Props = {
  /** icon to show in box */
  icon?: string;
};

withDefaults(defineProps<Props>(), { icon: "circle-info" });

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();
</script>

<style lang="scss" scoped>
.alert {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 40px;
  gap: 20px;
  border-radius: $rounded;
  background: $light-gray;

  .icon {
    color: $gray;
  }
}
</style>
