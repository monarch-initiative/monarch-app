import { configureAxe, getViolations, injectAxe } from "axe-playwright";
import { expect, test } from "@playwright/test";
import { log } from "../playwright.config";

log();

/** pages to test */
const paths = [
  "/",
  "/kg/about",
  "/kg/citation",
  "/kg/help",
  "/kg/status",
  "/results",
  "/kg/documentation",
  "/kg/downloads",
  "kg/terms",
  "/search-phenotypes",
  "/text-annotator",
  "/about/our-story",
  "/about/team",
  "/about/contact-us",
  "/about/sab",
  "/about/funding",
  "/about/publications",
];

/** axe rule overrides */
const rules = [
  /**
   * axe doesn't like light gray secondary text. also, color standards are not
   * always correct:
   *
   * https://uxmovement.com/buttons/the-myths-of-color-contrast-accessibility/
   * https://github.com/w3c/wcag/issues/695
   * https://twitter.com/DanHollick/status/1468958644364402702
   * https://github.com/Myndex/SAPC-APCA
   * https://twitter.com/DanHollick/status/1417895151003865090
   * https://twitter.com/argyleink/status/1329091518032867328
   */
  { id: "color-contrast", enabled: false },
  /** ignore select dropdowns that are appended to body */
  { id: "region", selector: ":not([role='listbox']" },
];

type Test = Parameters<typeof test>[1];

/** generic page axe test */
const checkPage =
  (path: string, selector?: string): Test =>
  async ({ page, browserName }) => {
    test.skip(browserName !== "chromium", "Only test Axe on chromium");

    /** navigate to page */
    await page.goto(path);

    /** wait for content to load */
    await page.waitForSelector("main");
    await page.waitForSelector("section");
    await page.waitForSelector("h1");
    await page.waitForTimeout(1000);

    /** setup axe */
    await injectAxe(page);
    await configureAxe(page, { rules });

    /** perform interaction on selector */
    if (selector) {
      await page.locator(selector).first().focus();
      await page.locator(selector).first().click();
    }

    /** axe check */
    const violations = await getViolations(page);
    const violationsMessage = JSON.stringify(violations, null, 2);
    expect(violationsMessage).toBe("[]");
  };

/** check all pages */
for (const path of paths) test("Accessibility check " + path, checkPage(path));

/** extra testbed component tests */
test(
  "Accessibility check /testbed (select single)",
  checkPage("/testbed", ".select-single button"),
);
test(
  "Accessibility check /testbed (select multi)",
  checkPage("/testbed", ".select-multi button"),
);
test(
  "Accessibility check /testbed (select tags)",
  checkPage("/testbed", ".select-tags input"),
);
test(
  "Accessibility check /testbed (select autocomplete)",
  checkPage("/testbed", ".select-autocomplete input"),
);
