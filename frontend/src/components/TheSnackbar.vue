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

<script setup lang="ts">
import { ref, computed } from "vue";
import { restartAnimations } from "@/util/dom";
import { useEventListener, useTimeoutFn } from "@vueuse/core";

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
function onPush(event: Event) {
  /** flash notification */
  if (element.value) restartAnimations(element.value);

  /** set notification text */
  text.value = (event as CustomEvent).detail;

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
