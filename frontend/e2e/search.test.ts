import { expect, test } from "@playwright/test";
import { log } from "../playwright.config";

log();

test("Recent/frequent results show", async ({ page }) => {
  await page.goto("/explore");

  const nodes = [
    "MONDO:0007523",
    "HP:0003179",
    "HP:0003179",
    "MONDO:0007523",
    "HP:0003179",
    "HP:0003179",
    "MONDO:0007523",
    "HP:0100775",
  ];

  for (const node of nodes) {
    await page.goto("/" + node);
    await expect(page.locator("#overview")).toBeVisible();
  }

  await page.goto("/explore");
  await page.locator("input").focus();
  const options = page.locator("[role='option']");

  /** recent */
  await expect(
    options
      .nth(0)
      .getByText(/Dural ectasia/i)
      .first(),
  ).toBeVisible();
  await expect(
    options
      .nth(1)
      .getByText(/Ehlers-Danlos syndrome, hypermobility/i)
      .first(),
  ).toBeVisible();
  await expect(
    options
      .nth(2)
      .getByText(/Protrusio acetabuli/i)
      .first(),
  ).toBeVisible();

  /** frequent */
  await expect(
    page
      .locator("[role='option']")
      .nth(3)
      .getByText(/Protrusio acetabuli/i)
      .first(),
  ).toBeVisible();
  await expect(
    page
      .locator("[role='option']")
      .nth(4)
      .getByText(/Ehlers-Danlos syndrome, hypermobility/i)
      .first(),
  ).toBeVisible();
});

test("Autocomplete results show", async ({ page }) => {
  /** type something in search box for regular backend autocomplete results */
  await page.goto("/explore");
  await page.locator("input").fill("Fanconi");
  await expect(
    page.getByText(/Fanconi renotubular syndrome/i).first(),
  ).toBeVisible();
});

test("Basic search results show", async ({ page }) => {
  await page.goto("/explore");
  await page.locator("input").fill("Fanconi");
  await page.locator("input").dispatchEvent("change");

  /** search result with link shows */
  const result = await page
    .getByRole("link")
    .filter({ hasText: /Fanconi anemia/i })
    .first();
  await expect(result).toHaveAttribute("href", /MONDO:0019391/i);
});

test("Pagination works", async ({ page }) => {
  await page.goto("/explore");
  await page.locator("input").fill("Fanconi");
  await page.locator("input").dispatchEvent("change");

  /** pagination text, and click through to next page */
  await expect(page.getByText(/1 to 20 of \d+ results/).first()).toBeVisible();
  await page.locator("button", { hasText: /^2$/ }).first().click();
  await expect(page.getByText(/11 to 30 of \d+ results/).first()).toBeVisible();
});

test("Filters show", async ({ page }) => {
  test.fixme(true, "Facets are not implemented on the backend yet");

  await page.goto("/explore");
  await page.locator("input").fill("Fanconi");
  await page.locator("input").dispatchEvent("change");

  /** filters show */
  /** actual filtering done by backend, so not much to test here */
  await page
    .getByText(/category/i)
    .first()
    .click();
  await expect(page.getByText(/disease*.25/i).first()).toBeVisible();
  await page.getByText(/taxon/i).first().click();
  await expect(page.getByText(/gallus gallus*.1/i).first()).toBeVisible();
});
