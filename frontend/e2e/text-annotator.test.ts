import { expect, test } from "@playwright/test";
/** https://github.com/microsoft/playwright/issues/23662 */
import example from "@/data/text-annotator.json" with { type: "json" };
import { log } from "../playwright.config";

log();

test("Basic search results show", async ({ page }) => {
  test.skip(true, "No fixture data yet");

  await page.goto("/explore#text-annotator");

  /** paste example text */
  await page.locator("textarea").focus();
  await page.locator("textarea").fill(example.content.slice(0, 100));
  await page.locator("textarea").blur();

  /** look for plain text result */
  await expect(page.getByText(/Lewis \(1978\) found 7/i).first()).toBeVisible();

  /** find first annotation and hover */
  await page
    .getByText(/affected/)
    .first()
    .dispatchEvent("mouseenter");

  /** look for links and text in tooltip */
  await expect(
    page
      .getByRole("link")
      .filter({ hasText: /HP:0032320/i })
      .first(),
  ).toHaveAttribute("href", /HP:0032320/i);
  await expect(
    page.getByText(/acts upstream of or within/i).first(),
  ).toBeVisible();
});
