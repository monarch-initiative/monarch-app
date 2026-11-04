<!--
  small info button that explains a nearby setting or value in a tooltip, on
  hover or focus
-->

<template>
  <AppButton
    v-tooltip="`<div>${text}</div>`"
    class="info-button"
    design="small"
    icon="circle-info"
    :aria-label="`About ${label}`"
  />
</template>

<script setup lang="ts">
import AppButton from "@/components/AppButton.vue";

type Props = {
  /**
   * explanation to show, may contain html. it's wrapped in one element so
   * inline tags like <b> stay in the flow of the text.
   */
  text: string;
  /** name of what is explained, for screen readers */
  label: string;
};

defineProps<Props>();
</script>

<style lang="scss" scoped>
.info-button {
  color: $gray;
  opacity: 0.6;
}

.info-button:hover,
.info-button:focus {
  opacity: 1;
}
</style>
