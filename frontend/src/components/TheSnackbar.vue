<!--
  temporary notification at bottom of screen
-->

<template>
  <Teleport to="body">
    <Transition name="fade">
      <!-- no-static-element-interactions rule is wrong here -->
      <!-- eslint-disable-next-line -->
      <div
        v-if="text"
        ref="element"
        role="alert"
        aria-live="polite"
        class="snackbar"
        @click="onClick"
      >
        {{ text }}
      </div>
    </Transition>
  </Teleport>
</template>

<script lang="ts">
/** push a notification to snackbar */
export const snackbar = (message: string): unknown =>
  window.dispatchEvent(new CustomEvent("snackbar", { detail: message }));
</script>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useEventListener, useTimeoutFn } from "@vueuse/core";
import { restartAnimations } from "@/util/dom";

/** current notification text */
const text = ref("");
/** notification element */
const element = ref<Element>();

/**
 * make hide delay longer for longer messages
 * https://ux.stackexchange.com/questions/22520/how-long-does-it-take-to-read-x-number-of-characters
 */
const delay = computed(() => 1500 + text.value.length * 100);
/** timer */
const { start, stop } = useTimeoutFn(() => (text.value = ""), delay);

/** on push notification event */
function onPush(event: CustomEvent) {
  /** flash notification */
  if (element.value) restartAnimations(element.value);

  /** set notification text */
  text.value = event.detail;

  /** set timer to close */
  start();
}

/** when user clicks notification */
function onClick() {
  stop();
  text.value = "";
}

/** listen for push notification event */
useEventListener(window, "snackbar", onPush);
</script>

<style lang="scss" scoped>
.snackbar {
  z-index: 99;
  position: fixed;
  bottom: 20px;
  left: 50%;
  padding: 10px;
  transform: translateX(-50%);
  border-radius: $rounded;
  background: $off-black;
  box-shadow: $shadow;
  color: $white;
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
