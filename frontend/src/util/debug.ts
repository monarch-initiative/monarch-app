/** wait ms */
export const sleep = async (ms = 0): Promise<void> =>
  new Promise((resolve) => globalThis.setTimeout(resolve, ms));

/** wait for repaint */
export const frame = async (): Promise<void> =>
  new Promise((resolve) => globalThis.requestAnimationFrame(() => resolve()));

/** try to synchronously/immutably log objects/proxies */
export const syncLog = (...args: unknown[]): void => {
  try {
    console.debug(...JSON.parse(JSON.stringify(args)));
  } catch (error) {
    console.debug("Couldn't log to console synchronously");
    console.debug(...args);
  }
};
