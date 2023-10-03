import { expect, test } from "@playwright/test";
import { log } from "../playwright.config";

log();

test("App renders", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#app")).not.toBeEmpty();
});
