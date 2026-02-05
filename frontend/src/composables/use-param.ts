import { ref, shallowRef, watch } from "vue";
import { type LocationQuery, type Router } from "vue-router";
import { cloneDeep, round } from "lodash";

/**
 * single "reactive" object url to sync with "raw" url. needed so we can batch
 * together multiple synchronous param sets into a single push/replace history
 * entry. vue-router does batch together multiple synchronous pushes/replaces,
 * but does not accommodate keeping/merging params, because currentRoute object
 * only updates at end of batch.
 */
export const url = ref<LocationQuery>({});

/** connect to router */
export function initRouter(router: Router) {
  /** flag to check if router.push/replace just occurred */
  let justPushed = false;

  /** when reactive url changes */
  watch(
    url,
    () => {
      /** push/replace based on mode */
      router[mode === "replace" ? "replace" : "push"]({
        /** update url to include params */
        query: cloneDeep(url.value),
        /** preserve hash */
        hash: router.currentRoute.value.hash,
      });
      justPushed = true;
    },
    { deep: true, immediate: true },
  );

  /** after raw url changes */
  router.afterEach((to) => {
    /**
     * if raw url just changed due to url object change, don't change url object
     * again
     */
    if (justPushed) return (justPushed = false);

    /** delete params in url object */
    for (const key of Object.keys(url.value))
      if (!to.query[key]) delete url.value[key];

    /** add/change params in url object */
    for (const [key, value] of Object.entries(to.query))
      url.value[key] = cloneDeep(value);
  });
}

/** how to update tab history */
const mode: "push" | "replace" = "push";

/** reactive variable 2-way-synced with param in url */
export function useParam<T>(
  key: string,
  { parse, stringify }: Param<T>,
  initialValue: T,
) {
  /** https://github.com/vuejs/composition-api/issues/483 */
  /** reactive "local" var that should act like slice of reactive "full" url */
  const variable = shallowRef(initialValue);

  watch(
    /** when param in full url object changes */
    () => url.value[key],
    () => {
      /** get updated value from url object */
      let newValue = "";
      /** if single value */
      if (typeof url.value[key] === "string") newValue = url.value[key];
      /** if multi-value, pick first */
      if (Array.isArray(url.value[key]) && url.value[key][0])
        newValue = url.value[key][0];

      /**
       * if key no longer there (e.g. user went back to url without it), reset
       * to initial value
       */
      if (!newValue) newValue = stringify(initialValue);

      /**
       * stringify process is sometimes "lossy" (e.g. rounding decimal places),
       * so compare values after that process and don't update if same
       */
      if (newValue === stringify(variable.value)) return;

      /** convert raw url string value to actual var value */
      variable.value = parse(newValue);
    },
    { immediate: true },
  );

  watch(
    /** when local var changes */
    variable,
    () => {
      /** convert actual var value to string for url */
      const newValue = stringify(variable.value);

      /** set url value */
      if (newValue) {
        if (Array.isArray(url.value[key]) && url.value[key][0])
          url.value[key][0] = newValue;
        else url.value[key] = newValue;
        /** if "empty", such as empty string or array, delete param from url */
      } else delete url.value[key];
    },
    /**
     * no "immediate", so url doesn't update until var changes from initial
     * value (presumably from user interaction)
     */
  );

  return variable;
}

/** generic parameter type, with methods to encode/decode to/from string (url) */
export type Param<P, S = P> = {
  parse: (value: string) => P;
  stringify: (value: S) => string;
};

/** treat param as string */
export const stringParam = (): Param<string> => ({
  parse: (value) => value,
  stringify: (value) => value,
});

/** treat param as number */
export const numberParam = (precision?: number): Param<number> => ({
  parse: (value) => Number(value) || 0,
  stringify: (value) => String(round(value || 0, precision)),
});

/** treat param as boolean */
export const booleanParam = (
  type: "number" | "string" = "number",
): Param<boolean> => ({
  parse: (value) =>
    value.toLowerCase() === (type === "string" ? "true" : "1") ? true : false,
  stringify: (value) => (type === "string" ? String(value) : value ? "1" : "0"),
});

/** higher-order array param of other params */
export const arrayParam = <T>(param: Param<T | undefined, T>): Param<T[]> => ({
  parse: (value) =>
    value
      .split(",")
      .map(param.parse)
      .filter((item): item is T => item !== undefined),
  stringify: (value) => value.map(param.stringify).join(","),
});
