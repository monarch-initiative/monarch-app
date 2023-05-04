<!--
  an icon, text, and link showing the status of something
-->

<template>
  <AppLink
    v-tooltip="code === 'error' ? 'See dev console for more details' : ''"
    :to="link || ''"
    class="status"
    :data-code="code || ''"
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
  paused: "pause-circle",
  success: "check-circle",
  warning: "exclamation-circle",
  error: "times-circle",
  unknown: "question-circle",
};

type Props = {
  /** status code */
  code: Code;
  /** link */
  link?: string;
};

const props = defineProps<Props>();

/** icon to show, associated with a status */
const icon = computed(() => icons[props.code]);
</script>

<style lang="scss" scoped>
.status {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 10px;
  text-decoration: none;
}

/** icon */

.icon {
  font-size: 1.5rem;
}

.status[data-code="loading"] .icon {
  color: $gray;
}

.status[data-code="paused"] .icon {
  color: $gray;
}

.status[data-code="success"] .icon {
  color: $success;
}

.status[data-code="warning"] .icon {
  color: $gray;
}

.status[data-code="error"] .icon {
  color: $error;
}

.status[data-code="unknown"] .icon {
  color: $gray;
}

/** text */

.text {
  text-align: left;
  color: $off-black;
  line-height: $spacing;
}

.note {
  color: $gray;
}
</style>
