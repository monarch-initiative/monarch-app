import type { PlaywrightTestConfig } from "@playwright/test";
import { devices } from "@playwright/test";

/** browsers to test when running locally */
const browsersLocal = [
  /* major browsers */
  {
    name: "chromium",
    use: { ...devices["Desktop Chrome"] },
  },
  {
    name: "webkit",
    use: { ...devices["Desktop Safari"] },
  },
  {
    name: "firefox",
    use: { ...devices["Desktop Firefox"] },
  },
];

/** browsers to test on CI */
const browsersCI = [
  {
    name: "chromium",
    use: { ...devices["Desktop Chrome"] },
  },
];

const config: PlaywrightTestConfig = {
  testDir: "./e2e",
  timeout: 30 * 1000,
  expect: {
    timeout: 5000,
  },
  reporter: "html",
  // https://github.com/microsoft/playwright/issues/19408#issuecomment-1347341819
  workers: process.env.CI ? 2 : undefined,

  /* shared settings for all projects below */
  use: {
    actionTimeout: 0,
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
    headless: true || !!process.env.CI,
  },

  /* browsers to test on */
  projects: process.env.CI ? browsersCI : browsersLocal,

  /* run local dev server before starting tests */
  webServer: {
    /** build instead of dev to more closely match production */
    command: "vite build --mode test && vite preview --port 5173",
    port: 5173,
  },
};

export default config;
