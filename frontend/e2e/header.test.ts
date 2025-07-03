import { expect, test } from "@playwright/test";

// Adjust viewport to simulate mobile and desktop
const mobileSize = { width: 375, height: 667 };
const desktopSize = { width: 1280, height: 800 };

test.describe("Header Navigation", () => {
  test("toggle menu works on mobile", async ({ page }) => {
    await page.setViewportSize(mobileSize);
    await page.goto("/");

    const toggle = page.locator("header button[aria-expanded]");
    const nav = page.locator("nav");

    // nav should be hidden initially
    await expect(nav).toBeHidden();

    // click to open menu
    await toggle.click();
    await expect(nav).toBeVisible();

    // click to close menu
    await toggle.click();
    await expect(nav).toBeHidden();
  });

  test("menu is visible on desktop", async ({ page }) => {
    await page.setViewportSize(desktopSize);
    await page.goto("/");

    const nav = page.locator("nav");
    await expect(nav).toBeVisible();
  });

  test("hero card is visible only on homepage desktop", async ({ page }) => {
    await page.setViewportSize(desktopSize);
    await page.goto("/");

    const heroCard = page.locator(".hero-card");
    await expect(heroCard).toBeVisible();
  });

  test("hero card does not show on mobile", async ({ page }) => {
    await page.setViewportSize(mobileSize);
    await page.goto("/");

    const heroCard = page.locator(".hero-card");
    await expect(heroCard).toHaveCount(0);
  });

  test("navigation contains dropdowns and links", async ({ page }) => {
    await page.setViewportSize(desktopSize);
    await page.goto("/");

    const navLinks = page.locator(".navItems .link");
    await expect(navLinks.first()).toBeVisible();

    const dropdowns = page.locator(".dropdown-button");
    const count = await dropdowns.count();
    expect(count).toBeGreaterThan(0);
  });
});
