import { useLocalStorage } from "@vueuse/core";
import type { Option } from "@/components/AppSelectAutocomplete.vue";

/** raw, in-order node history */
export const history = useLocalStorage<Option[]>("search-history", []);

/** add entry to node history */
export const addEntry = (entry: Option) => {
  history.value.push(entry);
};

/** delete entry(s) from node history */
export const deleteEntry = (entry: Option) =>
  (history.value = history.value.filter((e) => e.id !== entry.id));
