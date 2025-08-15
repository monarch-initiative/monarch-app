<template>
  <div class="toc-back" v-show="show">
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
import { onBeforeUnmount, onMounted, ref } from "vue";
import AppButton from "@/components/AppButton.vue";

const props = withDefaults(
  defineProps<{
    targetId?: string;
    thresholdVH?: number;
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

const show = ref(false);

const evaluate = () => {
  show.value = window.scrollY > window.innerHeight * props.thresholdVH;
};

const scrollTop = () => {
  const el = document.getElementById(props.targetId);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  else window.scrollTo({ top: 0, behavior: "smooth" });
};

onMounted(() => {
  evaluate();
  window.addEventListener("scroll", evaluate, { passive: true });
  window.addEventListener("resize", evaluate);
});
onBeforeUnmount(() => {
  window.removeEventListener("scroll", evaluate);
  window.removeEventListener("resize", evaluate);
});
</script>

<style scoped lang="scss">
.toc-back {
  display: flex;
  z-index: 1;
  justify-content: center;
  padding: 1em;
  border-bottom: 1px solid #e9eef0;
  background: #fff;
}
</style>
