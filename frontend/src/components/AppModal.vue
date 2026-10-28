<!--
  basic modal component with arbitrary content

  references:
  https://www.w3.org/TR/wai-aria-practices/examples/dialog-modal/dialog.html
-->

<template>
  <teleport to="body">
    <transition name="fade">
      <div v-if="modelValue" class="overlay">
        <!--
          The dim backdrop is a sibling of the dialog, not its parent. aria-hidden
          applies to a whole subtree, so while it sat on the wrapper the dialog was
          hidden along with it, and since #app is inert at the same time there was
          nothing left for a screen reader to reach. It also takes the outside-click
          dismissal, which is why the dialog no longer has to stop propagation.
        -->
        <div
          class="backdrop"
          aria-hidden="true"
          @mousedown="close"
          @touchstart="close"
        />
        <div
          ref="modal"
          class="modal"
          role="dialog"
          aria-modal="true"
          :aria-label="label"
        >
          <AppButton
            v-tooltip="'Close dialog (esc)'"
            class="close"
            design="circle"
            icon="xmark"
            @click="close"
          />
          <slot />
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script lang="ts">
/**
 * Open modals, oldest first.
 *
 * In a plain `<script>` because `<script setup>` runs its top level once per
 * instance, and this has to be shared: the decisions below are about the set of
 * open modals, not about any one of them. Only the topmost should react to
 * Escape, and the page behind should only become reachable again once the last
 * one closes. Previously every instance handled Escape and every close restored
 * the page, so with two open one keypress shut both, and dismissing the inner
 * one handed the background back to keyboard and screen readers while the outer
 * was still up.
 */
const stack: symbol[] = [];
</script>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, watch } from "vue";
import { disableBodyScroll, enableBodyScroll } from "body-scroll-lock";
import { useEventListener } from "@vueuse/core";

type Props = {
  /** two-way bound open state */
  modelValue?: boolean;
  /** modal aria label */
  label: string;
};

const props = defineProps<Props>();

type Emits = {
  /** two-way bound open state */
  "update:modelValue": [boolean];
};

const emit = defineEmits<Emits>();

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

/** element that had focus before modal was opened */
const originalFocus = ref<HTMLElement | null>(null);

/** modal element */
const modal = ref<HTMLElement>();

/** this instance's place in the stack */
const token = Symbol("modal");

/** update model value to close modal */
function close() {
  emit("update:modelValue", false);
}

/** whether this is the modal the user is currently looking at */
function isTopmost() {
  return stack[stack.length - 1] === token;
}

function keyDown(event: KeyboardEvent) {
  if (event.key !== "Escape") return;
  if (!props.modelValue || !isTopmost()) return;
  close();
}

useEventListener(window, "keydown", keyDown);

/** hide the page behind the modals from focus and screen readers */
function hideBackground() {
  const app = document.querySelector("#app");
  app?.setAttribute("aria-hidden", "true");
  app?.setAttribute("inert", "true");
}

/** give the page back, but only once nothing is stacked on top of it */
function showBackground() {
  if (stack.length) return;
  const app = document.querySelector("#app");
  app?.removeAttribute("aria-hidden");
  app?.removeAttribute("inert");
}

function release() {
  const index = stack.indexOf(token);
  if (index === -1) return;
  stack.splice(index, 1);
  if (modal.value) enableBodyScroll(modal.value);
  showBackground();
}

watch(
  () => props.modelValue,
  async (open) => {
    if (open) {
      originalFocus.value = document.activeElement as HTMLElement;
      stack.push(token);
      hideBackground();
      await nextTick();
      if (modal.value) disableBodyScroll(modal.value);
      /** focus first focusable element in modal */
      const query = "input, textarea, button, select";
      modal.value?.querySelector<HTMLElement>(query)?.focus();
    } else {
      release();
      await nextTick();
      /** restore focus to what had focus before modal opened */
      originalFocus.value?.focus();
    }
  },
  // immediate so a modal rendered already-open is handled too; without it such an
  // instance would never hide the page behind it or join the stack.
  { immediate: true },
);

/** a modal unmounted while open would otherwise leave the page inert forever */
onBeforeUnmount(release);
</script>

<style lang="scss" scoped>
.overlay {
  display: flex;
  z-index: 1100;
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  align-items: center;
  justify-content: center;
}

.backdrop {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  background: #000000c0;
}

.modal {
  display: flex;
  z-index: 1101;
  position: relative;
  flex-direction: column;
  align-items: center;
  max-width: min(800px, calc(100vw - 80px));
  max-height: calc(100vh - 80px);
  padding: 40px;
  overflow-y: auto;
  gap: 12px;
  background: $white;
}

/** close button */
.close {
  position: absolute;
  top: 10px;
  right: 10px;
  margin: 0;
  font-size: 0.8rem;
}
</style>
