import { snackbar } from "@/components/TheSnackbar.vue";

/** collapse whitespace in string */
export const collapse = (value = ""): string =>
  value.replace(/\s+/g, " ").trim();

/** insert html word break opportunities, for use on long strings such as urls */
export const breakUrl = (value = ""): string =>
  /** non-alphanumeric char followed by alphanumeric char */
  value.replaceAll(/([^A-Za-z0-9])([A-Za-z0-9])/g, "$1<wbr/>$2");

/** strip html from string */
export const stripHtml = (html = "") =>
  new DOMParser().parseFromString(html, "text/html").body.textContent || "";

/** format number value */
export const formatNumber = (value: number, compact = false) =>
  value
    .toLocaleString(undefined, {
      notation: compact ? "compact" : undefined,
    })
    .replace(/([^A-Za-z]+)([A-Za-z]+)/, "$1 $2");

/** safe copy to clipboard with notifications */
export const copyToClipboard = async (
  value: string,
  message = "Copied to clipboard",
) => {
  try {
    await window.navigator.clipboard.writeText(value);
    snackbar(message);
  } catch (error) {
    snackbar(`Error copying to clipboard. See dev console for more info.`);
    console.error(error);
  }
};
