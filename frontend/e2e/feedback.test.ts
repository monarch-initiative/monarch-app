import { expect, test } from "@playwright/test";

test("Feedback form can open and close", async ({ page }) => {
  /** setup */
  await page.goto("/");

  /** get open feedback form button */
  const open = page.locator(".float > button:last-child").first();

  /** open feedback form modal */
  await open.click();

  /** see if modal has opened and shown feedback form correctly */
  await expect(
    page
      .locator(".modal")
      .getByText(/Feedback Form/)
      .first(),
  ).toBeVisible();

  /** click in middle of modal, which should not close modal */
  await page.locator(".modal").first().click();
  await expect(page.locator(".modal")).toBeVisible();

  /** click in overlay in corner, which should close modal */
  await page
    .locator(".overlay")
    .first()
    .click({ position: { x: 10, y: 10 } });
  await expect(page.locator(".modal")).not.toBeVisible();

  /** reopen and make sure pressing esc closes */
  await open.click();
  await page.keyboard.press("Escape");
  await expect(page.locator(".modal")).not.toBeVisible();

  /** reopen and make sure x button closes */
  await open.click();
  await page.locator(".modal button").first().click();

  /** close button should always be first button in dom order */
  await expect(page.locator(".modal")).not.toBeVisible();
});
