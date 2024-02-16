<!--
  ring/arc/pie with number in middle
-->

<template>
  <div class="ring">
    <div>{{ score.toFixed(1) }}</div>
    <svg viewBox="-50 -50 100 100">
      <circle cx="0" cy="0" r="50" />
      <path :d="d" />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { clamp } from "lodash";
import { cos, sin } from "@/util/math";

type Props = {
  /** value to show in center of ring */
  score?: number;
  /** percent of ring filled (0-1) */
  percent?: number;
};

const props = withDefaults(defineProps<Props>(), {
  score: 0.5,
  percent: 0.5,
});

/** arc svg path */
const d = computed(() => {
  const angle = 360 * clamp(props.percent, 0.05, 0.95);
  const x = sin(angle) * 50;
  const y = -cos(angle) * 50;
  return `M 0 -50 A 50 50 0 ${angle >= 180 ? 1 : 0} 1 ${x} ${y}`;
});
</script>

<style lang="scss" scoped>
.ring {
  position: relative;
  flex-grow: 0;
  flex-shrink: 0;
  width: 45px;
  height: 45px;
  font-size: 0.9rem;

  & > * {
    display: flex;
    position: absolute;
    top: 0;
    left: 0;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
  }

  circle {
    fill: none;
    stroke: $light-gray;
    stroke-width: 10px;
  }

  path {
    fill: none;
    stroke: $theme;
    stroke-width: 10px;
  }
}
</style>
