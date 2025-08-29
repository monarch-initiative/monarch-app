<template>
  <div class="toc-top" v-show="show">
    <AppButton
      design="link"
      color="none"
      :text="label"
      icon="angle-up"
      icon-position="left"
      :aria-label="ariaLabel"
      @click="scrollTop"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useWindowScroll, useWindowSize } from "@vueuse/core";
import AppButton from "@/components/AppButton.vue";

// Props
const props = withDefaults(
  defineProps<{
    targetId?: string; // anchor to scroll to
    thresholdVH?: number; // show after this % of viewport
    label?: string;
    ariaLabel?: string;
  }>(),
  {
    targetId: "top",
    thresholdVH: 0.1,
    label: "Back to top",
    ariaLabel: "Back to top",
  },
);

// Reactive scroll/viewport
const { y } = useWindowScroll();
const { height } = useWindowSize();

// Show control after threshold
const show = computed(() => y.value > height.value * props.thresholdVH);

// Smooth scroll to anchor or page top
const scrollTop = () => {
  const el = document.getElementById(props.targetId);
  el
    ? el.scrollIntoView({ behavior: "smooth", block: "start" })
    : window.scrollTo({ top: 0, behavior: "smooth" });
};
</script>

<style scoped lang="scss">
.toc-top {
  display: flex;
  justify-content: center;
  padding: 1em;
  border-bottom: 1px solid #e9eef0;
  background: #fff;
  font-size: 0.8em;
}
</style>
