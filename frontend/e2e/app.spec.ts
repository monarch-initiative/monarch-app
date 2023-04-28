import { test, expect } from "@playwright/test";

test("App renders", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#app")).not.toBeEmpty();
});
