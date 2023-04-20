<!--
  temporary notification at bottom of screen
-->

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="text"
        ref="element"
        role="alert"
        aria-live="polite"
        class="snackbar"
        @click="onClick"
        @keydown="() => null"
      >
        {{ text }}
      </div>
    </Transition>
  </Teleport>
</template>

<script lang="ts">
/** Push a notification to snackbar */
export const snackbar = (message: string): unknown =>
  window.dispatchEvent(new CustomEvent("snackbar", { detail: message }));
</script>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useEventListener, useTimeoutFn } from "@vueuse/core";
import { restartAnimations } from "@/util/dom";

/** Current notification text */
const text = ref("");
/** Notification element */
const element = ref<Element>();

/**
 * Make hide delay longer for longer messages
 * https://ux.stackexchange.com/questions/22520/how-long-does-it-take-to-read-x-number-of-characters
 */
const delay = computed(() => 1500 + text.value.length * 100);
/** Timer */
const { start, stop } = useTimeoutFn(() => (text.value = ""), delay);

/** On push notification event */
function onPush(event: Event) {
  /** Flash notification */
  if (element.value) restartAnimations(element.value);

  /** Set notification text */
  text.value = (event as CustomEvent).detail;

  /** Set timer to close */
  start();
}

/** When user clicks notification */
function onClick() {
  stop();
  text.value = "";
}

/** Listen for push notification event */
useEventListener(window, "snackbar", onPush);
</script>

<style lang="scss" scoped>
.snackbar {
  position: fixed;
  bottom: 20px;
  left: 50%;
  padding: 10px;
  transform: translateX(-50%);
  background: $off-black;
  color: $white;
  box-shadow: $shadow;
  border-radius: $rounded;
  z-index: 99;
  animation: flash 0.25s linear forwards;
}

@keyframes flash {
  0% {
    background: $theme-dark;
  }
  100% {
    background: $off-black;
  }
}
</style>
