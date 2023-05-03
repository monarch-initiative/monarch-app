import type { Locator } from "@playwright/test";

// https://github.com/microsoft/playwright/issues/8114
export const paste = async (locator: Locator, value: string) => {
  await locator.fill(value);
  await locator.dispatchEvent("paste");
};
