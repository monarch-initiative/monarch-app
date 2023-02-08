/** wait */
export const sleep = async (ms = 0): Promise<void> =>
  new Promise((resolve) => window.setTimeout(resolve, ms));

/** try to synchronously/immutably log objects/proxies */
export const syncLog = (...args: Array<unknown>): void => {
  try {
    console.info(...JSON.parse(JSON.stringify(args)));
  } catch (error) {
    console.info("Couldn't log to console synchronously");
    console.info(...args);
  }
};
