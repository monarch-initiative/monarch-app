<!--
  ring/arc/pie with number in middle
-->

<template>
  <div v-tooltip="tooltip">
    <div v-if="type === 'ring'" class="ring">
      <svg viewBox="-50 -50 100 100">
        <circle class="back" cx="0" cy="0" r="50" />
        <path class="fill" :d="arc" />
      </svg>
      <b>
        <slot />
      </b>
    </div>

    <div v-if="type === 'bar'" class="bar">
      <b>
        <slot />
      </b>
      <svg viewBox="0 0 70 10">
        <rect class="back" x="0" y="0" width="100%" height="100%" />
        <rect
          class="fill"
          x="0"
          y="0"
          :width="`${100 * percent}%`"
          height="100%"
        />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { clamp } from "lodash";
import { cos, sin } from "@/util/math";

type Props = {
  /** percent filled (0-1) */
  percent?: number;
  /** design */
  type?: "ring" | "bar";
  /** tooltip on hover */
  tooltip?: string;
};

const props = withDefaults(defineProps<Props>(), {
  score: 0.5,
  percent: 0.5,
  type: "ring",
});

/** arc svg path */
const arc = computed(() => {
  /** https://stackoverflow.com/questions/5737975/circle-drawing-with-svgs-arc-path */
  const angle = 360 * clamp(props.percent, 0, 0.99999);
  const x = sin(angle) * 50;
  const y = -cos(angle) * 50;
  return `M 0 -50 A 50 50 0 ${angle >= 180 ? 1 : 0} 1 ${x} ${y}`;
});

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();
</script>

<style lang="scss" scoped>
.ring,
.bar {
  display: flex;
  flex-grow: 0;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 0.9rem;
}

.ring {
  position: relative;
  width: 40px;
  height: 40px;
  fill: none;
  stroke-width: 10px;

  & > * {
    position: absolute;
  }

  .back {
    stroke: $light-gray;
  }

  .fill {
    stroke: $theme;
  }
}

.bar {
  svg {
    height: 10px;
  }

  .back {
    fill: $light-gray;
  }

  .fill {
    fill: $theme;
  }
}
</style>
