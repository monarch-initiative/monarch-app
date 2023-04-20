<!--
  ring/arc/pie with number in middle
-->

<template>
  <div class="ring">
    <div>{{ score }}</div>
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
  /** range of score for normalization */
  min?: number;
  max?: number;
}

const props = withDefaults(defineProps<Props>(), {
  score: 50,
  min: 0,
  max: 100,
});

/** normalized score value */
const normalized = computed(() => {
  let value = (props.score - props.min) / (props.max - props.min);
  /** if max === min (essentially, if only one ring result to show in list) */
  if (Number.isNaN(value)) value = 0.5;
  return clamp(value, 0.05, 0.95);
});

/** arc svg path */
const d = computed(() => {
  const angle = 360 * normalized.value;
  const x = sin(angle) * 50;
  const y = -cos(angle) * 50;
  return `M 0 -50 A 50 50 0 ${angle >= 180 ? 1 : 0} 1 ${x} ${y}`;
});
</script>

<style lang="scss" scoped>
.ring {
  position: relative;
  width: 40px;
  height: 40px;
  flex-grow: 0;
  flex-shrink: 0;

  & > * {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
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
