import { expect, test } from "@playwright/test";

test("Homepage shows correct page title", async ({ page }) => {
  await page.goto("/");

  await expect(
    page.getByRole("heading", { name: /what is monarch initiative/i }),
  ).toBeVisible();
});
