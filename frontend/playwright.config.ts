import type { PlaywrightTestConfig } from "@playwright/test";
import { devices } from "@playwright/test";

const config: PlaywrightTestConfig = {
  testDir: "./e2e",
  timeout: 30 * 1000,
  expect: {
    timeout: 5000,
  },
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",

  /* Shared settings for all projects below */
  use: {
    actionTimeout: 0,
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
    headless: true || !!process.env.CI,
  },

  /* Major browsers */
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
      testMatch: /^((?!axe).)*$/,
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
      testMatch: /^((?!axe).)*$/,
    },
  ],

  /* Run local dev server before starting tests */
  webServer: {
    /**
     * Use the dev server by default for faster feedback loop. Use the preview
     * server on CI for more realistic testing
     */
    command: process.env.CI
      ? "vite preview --port 5173 --mode test"
      : "vite dev --mode test",
    port: 5173,
    reuseExistingServer: !process.env.CI,
  },
};

export default config;
