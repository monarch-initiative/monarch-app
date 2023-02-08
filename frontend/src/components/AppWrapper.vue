<!-- 
  component to conditionally wrap slot content in tag
-->

<template>
  <component :is="tag" v-if="wrap">
    <slot />
  </component>
  <slot v-else />
</template>

<script setup lang="ts">
interface Props {
  /** tag */
  tag: string;
  /** wrap */
  wrap: boolean;
}

defineProps<Props>();
</script>
