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
