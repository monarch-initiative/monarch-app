<!--
  ring/arc/pie with number in middle
-->

<template>
  <div v-if="props.type === `ring`" class="ring">
    <b>{{ score.toFixed(1) }}</b>
    <svg viewBox="-50 -50 100 100">
      <circle cx="0" cy="0" r="50" />
      <path :d="d" />
    </svg>
  </div>
  
  <div v-else class="bar">
    <svg viewBox="-50 -50 100 30">
      <rect
      x="-50"
      y="-50"
      rx="3"
      width="100%"
      height="100%"
      fill="none"
      />
      <rect
      x="-49"
      y="-49"
      rx="3"
      :width="fillWidth"
      height="95%"
      fill="none"
      class="fill"
      />
    </svg>
    <b>{{ score.toFixed(1) }}</b>
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
  type?: "bar" | "ring";
};

const props = withDefaults(defineProps<Props>(), {
  score: 0.5,
  percent: 0.5,
  type: "ring",
});

/** arc svg path */
const d = computed(() => {
  /** https://stackoverflow.com/questions/5737975/circle-drawing-with-svgs-arc-path */
  const angle = 360 * clamp(props.percent, 0, 0.99999);
  const x = sin(angle) * 50;
  const y = -cos(angle) * 50;
  return `M 0 -50 A 50 50 0 ${angle >= 180 ? 1 : 0} 1 ${x} ${y}`;
});

const fillWidth = computed(() => `${clamp(props.percent*100, 0, 98)}%`);
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

.bar {
  position: relative;
  flex-grow: 0;
  flex-shrink: 0;
  width: 90px;
  height: 30px;
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

  rect {
    fill: none;
    stroke: $light-gray;
    stroke-width: 3px;
    &.fill {
      fill: $theme;
      stroke: none;
    }
  }
}
</style>
