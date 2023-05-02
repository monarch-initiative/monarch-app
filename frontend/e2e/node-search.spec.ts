import { expect, test } from "@playwright/test";

test("Redirects to explore page from home page", async ({ page }) => {
  /** go to homepage and focus search box */
  await page.goto("/");
  await page.locator("input").focus();
  const loc = new URL(page.url());
  expect(loc.pathname).toBe("/explore");

  /** go to homepage and click one of tabs */
  await page.goto("/");
  await page
    .getByText(/Text Annotator/)
    .first()
    .click();
  const { pathname } = new URL(page.url());
  expect(pathname).toBe("/explore");
});

test("Recent/frequent results show", async ({ page }) => {
  await page.goto("/explore");

  /** dummy searches */
  const searches = [
    "abc def",
    "123",
    "123",
    "abc def",
    "123",
    "123",
    "abc def",
  ];

  /** go through dummy searches */
  for (const search of searches) {
    await page.locator("input").fill(search);
    /** dispatch textbox change event which triggers search and records it */
    await page.locator("input").dispatchEvent("change");
    /** wait for results */
    await expect(page.locator("p.description").first()).toBeVisible();
    await page.locator(".textbox button").click();
  }

  /** go to node page, which should also get added to search history */
  await page.goto("/disease/MONDO:12345");
  /** wait for page to load */
  await expect(page.locator("#overview")).toBeVisible();
  await page.goto("/explore");

  /** focus search box to show list of results */
  await page.locator("input").focus();

  /** recent */
  const options = page.locator("[role='option']");
  await expect(
    options
      .nth(0)
      .getByText(/marfan syndrome/i)
      .first()
  ).toBeVisible();
  await expect(
    options
      .nth(1)
      .getByText(/abc def/i)
      .first()
  ).toBeVisible();
  await expect(options.nth(2).getByText(/123/).first()).toBeVisible();

  /** frequent */
  await expect(
    page.locator("[role='option']").nth(3).getByText(/123/).first()
  ).toBeVisible();
  await expect(
    page
      .locator("[role='option']")
      .nth(4)
      .getByText(/abc def/)
      .first()
  ).toBeVisible();
});

test("Autocomplete results show", async ({ page }) => {
  /** type something in search box for regular backend autocomplete results */
  await page.goto("/explore");
  await page.locator("input").fill("Marfan");
  await expect(
    page.getByText(/Marfan and Marfan-related disorder/).first()
  ).toBeVisible();
});

test("Basic search results show", async ({ page }) => {
  await page.goto("/explore");
  await page.locator("input").fill("Marfan");
  await page.locator("input").dispatchEvent("change");

  /** search result with link shows */
  const result = await page
    .getByRole("link")
    .filter({ hasText: /neonatal marfan syndrome/i })
    .first();
  await expect(result).toHaveAttribute("href", "/disease/MONDO:0017309");
});

test("Pagination works", async ({ page }) => {
  await page.goto("/explore");
  await page.locator("input").fill("Marfan");
  await page.locator("input").dispatchEvent("change");

  /** pagination text, and click through to next page */
  await expect(page.getByText(/1 to 10 of 61 results/).first()).toBeVisible();
  await page.locator("button", { hasText: /^2$/ }).first().click();
  await expect(page.getByText(/11 to 20 of 61 results/).first()).toBeVisible();
});

test("Filters show", async ({ page }) => {
  await page.goto("/explore");
  await page.locator("input").fill("Marfan");
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
