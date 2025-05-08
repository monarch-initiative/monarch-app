import { expect, test } from "@playwright/test";
import { log } from "../playwright.config";

log();

test("Header nav bar collapses on small screens", async ({ page }) => {
  /** setup */
  await page.goto("/");
  await page.setViewportSize({ width: 320, height: 568 });

  await page.evaluate(() => window.dispatchEvent(new Event("resize")));
  /** get elements of interest */
  const toggle = page.locator("header button").first();
  const nav = page.locator("nav").first();

  /** click toggle button and see if nav hides/shows */
  await expect(toggle).toBeVisible();
  await expect(nav).not.toBeVisible();
  await toggle.click();
  await expect(nav).toBeVisible();
  await toggle.click();
  await expect(nav).not.toBeVisible();
});
