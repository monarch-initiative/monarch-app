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

test("Similarity Search: untouched settings send only the metric", async ({
  page,
}) => {
  await page.goto("/search-phenotypes");
  await page.getByRole("button", { name: /Similarity Search/i }).click();
  await page
    .getByText(/example/i)
    .first()
    .click();

  const request = page.waitForRequest("**/semsim/search*");
  await page
    .getByRole("button", { name: /Analyze/i })
    .first()
    .click();
  const body = (await request).postDataJSON();
  expect(Object.keys(body).sort()).toEqual(["group", "metric", "termset"]);
});

test("Similarity Search: phenotypes and settings load from the url", async ({
  page,
}) => {
  await page.goto(
    "/search-phenotypes?phenotypes=HP:0001250,HP:0003186&directionality=object_to_subject",
  );
  await expect(page.locator(".select-tags > .box > button")).toHaveCount(2);
  await expect(page.getByText("HP:0003186")).toBeVisible();

  const request = page.waitForRequest("**/semsim/search*");
  await page
    .getByRole("button", { name: /Analyze/i })
    .first()
    .click();
  const body = (await request).postDataJSON();
  expect(body.termset).toEqual(["HP:0001250", "HP:0003186"]);
  expect(body.directionality).toBe("object_to_subject");
});

test("Similarity Search: chosen phenotypes are kept in the url", async ({
  page,
}) => {
  await page.goto("/search-phenotypes");
  await page.getByRole("button", { name: /Similarity Search/i }).click();
  await page
    .getByText(/example/i)
    .first()
    .click();
  await expect(page).toHaveURL(/phenotypes=HP/);
});

test("Similarity Search: too many phenotypes for a url are left out of it", async ({
  page,
}) => {
  await page.goto("/search-phenotypes?directionality=object_to_subject");
  const ids = Array.from(
    { length: 600 },
    (_, index) => `HP:${String(index).padStart(7, "0")}`,
  );
  await paste(page.locator(".select-tags input"), ids.join(","));
  await expect(page.locator(".select-tags > .box > button")).toHaveCount(600);
  await expect(page).toHaveURL(/directionality=object_to_subject/);
  expect(page.url()).not.toContain("phenotypes=");
});
