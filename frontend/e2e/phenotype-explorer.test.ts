import type { Locator } from "@playwright/test";
import { expect, test } from "@playwright/test";

// helper to simulate paste action
export const paste = async (locator: Locator, value: string) => {
  await locator.fill(value);
  await locator.dispatchEvent("paste");
};

test("Similarity Search: Populating example works", async ({ page }) => {
  await page.goto("/search-phenotypes");

  // switch to 'Similarity Search' tab
  await page.getByRole("button", { name: /Similarity Search/i }).click();

  // click example button and expect multiple tags to appear
  await page
    .getByText(/example/i)
    .first()
    .click();
  const count = await page.locator(".select-tags > .box > button").count();
  expect(count).toBeGreaterThan(5);
});

// test("Similarity Compare: Phenotype set vs set", async ({ page }) => {
//   await page.goto("/search-phenotypes");

//   // switch to 'Similarity Compare' tab
//   await page.getByRole("button", { name: /Similarity Compare/i }).click();

//   // paste phenotypes into both input boxes
//   await paste(
//     page.locator("input").first(),
//     "HP:0004970,HP:0004933,HP:0004927",
//   );
//   await paste(page.locator("input").last(), "HP:0004970,HP:0004933,HP:0004927");

//   // click analyze and verify result
//   await page
//     .getByText(/Analyze/i)
//     .first()
//     .click();
//   await expect(page.getByText(/female sterile/i)).toBeVisible();
// });
