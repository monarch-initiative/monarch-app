<!--
  an icon, text, and link showing the status of something
-->

<template>
  <AppLink
    v-tooltip="code === 'error' ? 'See dev console for more details' : ''"
    :to="link || ''"
    :class="['status', code]"
    :aria-label="code || ''"
  >
    <AppIcon class="icon" :icon="icon" />
    <span class="text">
      <slot />
    </span>
  </AppLink>
</template>

<script lang="ts">
/** possible status codes */
export const Codes = [
  "loading",
  "success",
  "warning",
  "error",
  "paused",
  "unknown",
] as const;

export type Code = (typeof Codes)[number];
</script>

<script setup lang="ts">
import { computed } from "vue";

/** icons for status codes */
const icons: Record<Code, string> = {
  loading: "loading",
  paused: "circle-pause",
  success: "circle-check",
  warning: "circle-exclamation",
  error: "circle-xmark",
  unknown: "circle-question",
};

type Props = {
  /** status code */
  code: Code;
  /** link */
  link?: string;
};

const props = defineProps<Props>();

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

/** icon to show, associated with a status */
const icon = computed(() => icons[props.code]);
</script>

<style lang="scss" scoped>
.status {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  gap: 20px;
  text-decoration: none;
}

/** icon */

.icon {
  font-size: 1.5rem;
}

.status.loading .icon {
  color: $gray;
}

.status.paused .icon {
  color: $gray;
}

.status.success .icon {
  color: $success;
}

.status.warning .icon {
  color: $gray;
}

.status.error .icon {
  color: $error;
}

.status.unknown .icon {
  color: $gray;
}

/** text */

.text {
  color: $off-black;
  line-height: $spacing;
  text-align: left;
}

.note {
  color: $gray;
}
</style>
