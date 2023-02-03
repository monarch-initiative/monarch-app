<!--
  buttons that float on side of page for handy functions
-->

<template>
  <div class="float" :style="{ bottom: nudge + 'px' }">
    <transition name="fade">
      <AppButton
        v-if="showJump"
        v-tooltip="'Jump to top of page'"
        design="circle"
        class="button"
        icon="angle-up"
        @click="jump()"
      />
    </transition>
    <transition name="fade">
      <AppButton
        v-if="showFeedback"
        v-tooltip="'Give us feedback on this page!'"
        design="circle"
        class="button"
        icon="comment"
        @click="showModal = true"
      />
    </transition>
    <AppModal v-model="showModal" label="Feedback form">
      <TheFeedbackForm :modal="true" />
    </AppModal>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from "vue";
import { useRoute } from "vue-router";
import {
  useEventListener,
  useMutationObserver,
  useActiveElement,
} from "@vueuse/core";
import AppModal from "@/components/AppModal.vue";
import TheFeedbackForm from "@/components/TheFeedbackForm.vue";

/** route info */
const route = useRoute();

/** focused element */
const focused = useActiveElement();

/** whether to show jump button */
const showJump = ref(false);
/** whether to show feedback form button */
const showFeedback = ref(true);
/** whether to show feedback modal */
const showModal = ref(false);
/** how much to push buttons upward to make room for footer if in view */
const nudge = ref(0);

/** update data state */
async function update() {
  /** wait for rendering to finish */
  await nextTick();

  /** whether some kind of input/textbox/control focused */
  const controlFocused =
    focused.value && focused.value.matches("input, textarea");

  /** get dimensions of footer */
  const footerEl = document?.querySelector("footer");
  if (!footerEl) return;
  const footer = footerEl.getBoundingClientRect();

  /** show jump button if user has scrolled far down enough */
  showJump.value = !controlFocused && window.scrollY > window.innerHeight * 0.1;
  /** show feedback button if user not already on dedicated feedback page */
  showFeedback.value =
    !controlFocused && String(route.name || "").toLowerCase() !== "feedback";

  /** calculate nudge */
  nudge.value = Math.max(0, footer.height + window.innerHeight - footer.bottom);
}

/** jump to top of page */
function jump() {
  window.scrollTo(0, 0);
}

/** run update on: page load, route change, focused, scroll, resize, reflow, etc. */
onMounted(update);
watch(route, update, { deep: true });
watch(focused, update);
useEventListener(window, "scroll", update);
useEventListener(window, "resize", update);
useMutationObserver(document?.body, update, {
  subtree: true,
  childList: true,
});
</script>

<style lang="scss" scoped>
.float {
  --spacing: 10px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: flex-end;
  gap: var(--spacing);
  position: fixed;
  right: 0;
  padding: var(--spacing);
  z-index: 20;
}

.button {
  font-size: 0.9rem;
}
</style>
