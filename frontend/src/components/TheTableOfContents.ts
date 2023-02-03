/** close the table of contents panel */
export const closeToc = (): unknown =>
  window.dispatchEvent(new CustomEvent("closetoc"));
