import { ref } from "vue";

/**
 * whether the user has acknowledged that the drug sections are for research use
 * only. Shared by every drug section on the page and remembered for the browser
 * session, so the notice gates them once rather than on every page.
 */
const KEY = "drug-sections-research-use-acknowledged";

const read = (): boolean => {
  try {
    return window.sessionStorage.getItem(KEY) === "true";
  } catch {
    return false;
  }
};

const acknowledged = ref(read());

export const useResearchUseAcknowledgement = () => ({
  acknowledged,
  acknowledge: () => {
    acknowledged.value = true;
    try {
      window.sessionStorage.setItem(KEY, "true");
    } catch {
      /* storage unavailable (private window, blocked site data): this page only */
    }
  },
});
