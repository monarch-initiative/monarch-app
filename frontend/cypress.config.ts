import { defineConfig } from "cypress";

export default defineConfig({
  video: false,
  fixturesFolder: "tests/fixtures",
  screenshotsFolder: "tests/e2e/screenshots",
  videosFolder: "tests/e2e/videos",
  e2e: {
    specPattern: "tests/e2e/specs/**/*.cy.{js,jsx,ts,tsx}",
    supportFile: "tests/e2e/support/index.js",

    /** https://github.com/cypress-io/cypress/issues/3199#issuecomment-529430701 */
    setupNodeEvents(on) {
      on("task", {
        log(message) {
          console.log(message);
          return null;
        },
      });
    },
  },
});
