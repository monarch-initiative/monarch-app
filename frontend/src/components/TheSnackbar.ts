/** push a notification to snackbar */
export const snackbar = (message: string): unknown =>
  window.dispatchEvent(new CustomEvent("snackbar", { detail: message }));
