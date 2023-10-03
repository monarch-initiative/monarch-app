import type { PlaywrightTestConfig } from "@playwright/test";
import test, { devices } from "@playwright/test";

/** pass browser console logs to cli logs */
export const log = () => {
  if (process.env.RUNNER_DEBUG)
    test.beforeEach(({ page }) =>
      page.on("console", (msg) => console.log(msg.text())),
    );
};

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
    /**
     * vite uses esbuild for dev but parcel for build. results should be the
     * same except for very rare cases (like the very old phenogrid). cover both
     * situations w/ local and CI. of the two, build should be more reflective
     * of actual production app.
     */
    command: process.env.CI
      ? "vite build --mode test && vite preview --port 5173"
      : "vite dev --mode test",
    port: 5173,
  },
};

export default config;
