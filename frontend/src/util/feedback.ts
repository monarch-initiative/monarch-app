import parser from "ua-parser-js";

/** automatic details recorded with feedback: the page and the user's browser */
export const feedbackDetails = (page: string) => {
  /** get browser/device/os/etc details from ua parser library */
  const { browser, device, os, engine, cpu } = parser();

  /** filter and join strings together */
  const concat = (...array: (string | undefined)[]) =>
    array.filter((e) => e && e !== "()").join(" ");

  /** make map of desired properties in desired stringified format */
  return {
    Page: page,
    Browser: concat(browser.name, browser.version),
    Device: concat(device.vendor, device.model, device.type),
    OS: concat(os.name, os.version, cpu.architecture),
    Engine: concat(engine.name, engine.version),
  };
};
