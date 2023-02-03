import { useLocalStorage } from "@vueuse/core";

/** raw, in-order node search/visit history */
export const history = useLocalStorage<Array<string>>(
  "node-search-history",
  []
);

/** add entry to node search/visit history */
export const addEntry = (value?: string) => {
  if (value?.trim()) history.value.push(value.trim());
};

/** delete entry(s) from node search/visit history */
export const deleteEntry = (value: string) =>
  (history.value = history.value.filter(
    (entry) => entry.trim() !== value.trim()
  ));
