import { nextTick, onMounted, ref, watchEffect } from "vue";
import {
  useMutationObserver,
  useResizeObserver,
  useScroll,
} from "@vueuse/core";

/** add classes to element when scrollable for styling */
export const useScrollable = () => {
  const element = ref<HTMLElement>();
  const { arrivedState } = useScroll(element);

  /** set css class on/off */
  function setClass(_class: string, on: boolean) {
    element.value?.classList?.[on ? "remove" : "add"](_class);
  }

  /** set classes */
  watchEffect(() => {
    if (!element.value) return;
    const { left, right } = arrivedState;
    setClass("scrollable-left", left);
    setClass("scrollable-right", right);
  });

  /** force table scroll to update */
  async function updateScroll() {
    await nextTick();
    element.value?.dispatchEvent(new Event("scroll"));
  }

  /** update scroll on some events that might affect element's scrollWidth/Height */
  onMounted(updateScroll);
  useResizeObserver(element, updateScroll);
  useMutationObserver(element, updateScroll, {
    childList: true,
    subtree: true,
  });

  return { ref: element, arrivedState, updateScroll };
};
