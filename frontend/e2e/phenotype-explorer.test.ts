import type { Locator } from "@playwright/test";
import { expect, test } from "@playwright/test";

// https://github.com/microsoft/playwright/issues/8114
export const paste = async (locator: Locator, value: string) => {
  await locator.fill(value);
  await locator.dispatchEvent("paste");
};

test("Populating example works", async ({ page }) => {
  await page.goto("/explore#phenotype-explorer");

  /** click example button, check tags select component has selected entries */
  await page
    .getByText(/example/)
    .first()
    .click();
  await expect(
    await page.locator(".select-tags > .box > button").count(),
  ).toBeGreaterThan(5);
});

test("Mode switching works", async ({ page }) => {
  await page.goto("/explore#phenotype-explorer");

  /** really just check that all appropriate options show in select */
  await page
    .locator("button", { hasText: /these phenotypes/i })
    .first()
    .click();
  await page
    .locator("[role='option'] > *", { hasText: /all human diseases/i })
    .first()
    .click();
  await page
    .locator("button", { hasText: /all human diseases/i })
    .first()
    .click();
  await page
    .locator("[role='option'] > *", { hasText: /all genes/i })
    .first()
    .click();
  await page
    .locator("button", { hasText: /all genes/i })
    .first()
    .click();
});

/**
 * in these tests, test that phenogrid appears, but do not test phenogrid
 * functionality itself, as that is in the scope of the phenogrid repo
 */

test("Phenotype set vs gene/disease works", async ({ page }) => {
  test.skip(true, "API endpoint not implemented yet");

  await page.goto("/explore#phenotype-explorer");

  /** go to right mode */
  await page
    .locator("button", { hasText: /these phenotypes/i })
    .first()
    .click();
  await page
    .locator("[role='option'] > *", { hasText: /all genes/i })
    .first()
    .click();

  /** paste specific dummy phenotypes */
  await paste(page.locator("input"), "HP:0004970,HP:0004933,HP:0004927");

  /** run analysis, and look for expected results */
  await page
    .getByText(/Analyze/i)
    .first()
    .click();
  await expect(page.getByText(/55/i).first()).toBeVisible();
  await expect(page.getByText(/1600029I14Rik/i).first()).toBeVisible();
  await expect(page.getByText(/Mus musculus/i).first()).toBeVisible();
});

test("Phenotype set vs phenotype set works", async ({ page }) => {
  test.skip(true, "Fixture data not stable yet");

  await page.goto("/explore#phenotype-explorer");

  /** paste specific dummy phenotypes */
  await paste(
    page.locator("input").first(),
    "HP:0004970,HP:0004933,HP:0004927",
  );
  await paste(page.locator("input").last(), "HP:0004970,HP:0004933,HP:0004927");

  /** run analysis, and look for expected results */
  await page
    .getByText(/Analyze/)
    .first()
    .click();
  await expect(page.getByText(/0/).first()).toBeVisible();
  await expect(page.getByText(/female sterile/).first()).toBeVisible();
});
