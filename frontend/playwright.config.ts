import type { PlaywrightTestConfig } from "@playwright/test";
import { devices } from "@playwright/test";

const config: PlaywrightTestConfig = {
  testDir: "./e2e",
  timeout: 30 * 1000,
  expect: {
    timeout: 5000,
  },
  // https://github.com/microsoft/playwright/issues/19408
  reporter: "html",

  /* shared settings for all projects below */
  use: {
    actionTimeout: 0,
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
    headless: true || !!process.env.CI,
  },

  /* major browsers */
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    // {
    //   name: "firefox",
    //   use: { ...devices["Desktop Firefox"] },
    //   testMatch: /^((?!axe).)*$/,
    // },
    // {
    //   name: "webkit",
    //   use: { ...devices["Desktop Safari"] },
    //   testMatch: /^((?!axe).)*$/,
    // },
  ],

  /* run local dev server before starting tests */
  webServer: {
    /**
     * use the dev server by default for faster feedback loop. Use the preview
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
