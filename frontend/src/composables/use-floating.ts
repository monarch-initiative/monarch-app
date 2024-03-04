import type { CSSProperties, Ref } from "vue";
import { ref } from "vue";
import { debounce } from "lodash";
import { computePosition, flip, shift, size } from "@floating-ui/dom";
import { useEventListener } from "@vueuse/core";

/** use floating-ui to position dropdown */

export const useFloating = (
  anchor: Ref<HTMLElement>,
  dropdown: Ref<HTMLElement>,
  fit = false,
) => {
  /** style of dropdown */
  const style = ref<CSSProperties>({
    position: "absolute",
    left: "0px",
    top: "0px",
    minWidth: "0px",
  });

  /** floating-ui options */
  const options = {
    middleware: [
      flip(),
      shift({ padding: 5 }),
      size({
        /** update min width based on target width */
        apply: ({ rects }) => {
          if (fit) style.value.width = rects.reference.width + "px";
          else style.value.minWidth = rects.reference.width + "px";
        },
      }),
    ],
  };

  /** func to recompute position on command */
  async function calculate() {
    /** make sure we have needed element references */
    if (!anchor.value || !dropdown.value) return;

    /** use floating-ui to compute position of dropdown */
    const { x, y } = await computePosition(
      anchor.value,
      dropdown.value,
      options,
    );

    /** set style from position */
    style.value.left = x + "px";
    style.value.top = y + "px";
  }

  /** automatically run calculate on reflow events */
  const debounced = debounce(calculate, 100);
  useEventListener(window, "scroll", debounced);
  useEventListener(window, "resize", debounced);

  return { calculate, style };
};
