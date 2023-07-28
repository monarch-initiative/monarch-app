import { sleep } from "../src/util/debug";
import { expect, test } from "@playwright/test";

test("Document title updates on navigation", async ({ page }) => {
  /** pages to test */
  const pages = ["explore", "about", "help"];

  /** visit each page and check doc title */
  for (const _page of pages) {
    await page.goto("/" + _page);
    await sleep(100);
    await expect(page).toHaveTitle(/monarch/i);
    await expect(page).toHaveTitle(new RegExp(_page, "i"));
  }
});
