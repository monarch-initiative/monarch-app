import type { Locator, Page } from "@playwright/test";

// https://github.com/microsoft/playwright/issues/8114
const modifier = process.platform === "darwin" ? "Meta" : "Control";
export const paste = async (page: Page, locator: Locator, value: string) => {
  page.evaluate(`navigator.clipboard.writeText("${value}")`);
  await locator.press(`${modifier}+KeyV`);
};
