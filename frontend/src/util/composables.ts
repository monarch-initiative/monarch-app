import type { CSSProperties, Ref } from "vue";
import { ref, shallowRef } from "vue";
import { debounce } from "lodash";
import { computePosition, flip, shift, size } from "@floating-ui/dom";
import { useEventListener } from "@vueuse/core";

/**
 * Inspired by react-query. simple query manager/wrapper for making queries in
 * components. reduces repetitive boilerplate code for loading/error states,
 * try/catch blocks, de-duplicating requests, etc.
 */
export const useQuery = <Data, Args extends Array<unknown>>(
  /**
   * Main async func that returns data. should be side-effect free to avoid race
   * conditions, because multiple can be running at same time.
   */
  func: (...args: Args) => Promise<Data>,
  /** Default value used for data before done loading and on error. */
  defaultValue: Data,
  /**
   * Func to run on success. use for side effects. only gets called on latest of
   * concurrent runs.
   */
  onSuccess?: (
    /** Response data */
    response: Data,
    /** Props passed to main func */
    props: Args
  ) => void
) => {
  /** Query state/status */
  const isLoading = ref(false);
  const isError = ref(false);
  const isSuccess = ref(false);

  /** Query results */
  /** https://github.com/vuejs/composition-api/issues/483 */
  const data = shallowRef<Data>(defaultValue);

  /** Latest query id, unique to this useQuery instance */
  let latest;

  /** Wrapped query function */
  async function query(...args: Args): Promise<void> {
    try {
      /** Unique id for current run */
      const current = Symbol();
      latest = current;

      /** Reset state */
      isLoading.value = true;
      isError.value = false;
      isSuccess.value = false;
      data.value = defaultValue;

      /** Run provided function */
      const result = await func(...args);

      /** If this run still the latest */
      if (current === latest) {
        /** Assign results to data */
        data.value = result;

        /** Update state */
        isLoading.value = false;
        isSuccess.value = true;

        /** On success callback */
        if (onSuccess) onSuccess(result, args);
      } else {
        /** Otherwise, log special "stale" error */
        console.error("Stale query");
      }
    } catch (error) {
      /** Log error */
      console.error(error);

      /** Update state */
      isError.value = true;
      isLoading.value = false;
    }
  }

  return { query, data, isLoading, isError, isSuccess };
};

/** Use floating-ui to position dropdown */
export const useFloating = (
  anchor: Ref<HTMLElement>,
  dropdown: Ref<HTMLElement>,
  fit = false
) => {
  /** Style of dropdown */
  const style = ref<CSSProperties>({
    position: "absolute",
    left: "0px",
    top: "0px",
    minWidth: "0px",
  });

  /** Floating-ui options */
  const options = {
    middleware: [
      flip(),
      shift({ padding: 5 }),
      size({
        /** Update min width based on target width */
        apply: ({ rects }) => {
          if (fit) style.value.width = rects.reference.width + "px";
          else style.value.minWidth = rects.reference.width + "px";
        },
      }),
    ],
  };

  /** Func to recompute position on command */
  async function calculate() {
    /** Make sure we have needed element references */
    if (!anchor.value || !dropdown.value) return;

    /** Use floating-ui to compute position of dropdown */
    const { x, y } = await computePosition(
      anchor.value,
      dropdown.value,
      options
    );

    /** Set style from position */
    style.value.left = x + "px";
    style.value.top = y + "px";
  }

  /** Automatically run calculate on reflow events */
  const debounced = debounce(calculate, 100);
  useEventListener(window, "scroll", debounced);
  useEventListener(window, "resize", debounced);

  return { calculate, style };
};
