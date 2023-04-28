import { createApp } from "vue";
import VueGtag from "vue-gtag";
import Hotjar from "vue-hotjar";
import { BrowserTracing } from "@sentry/browser";
import * as Sentry from "@sentry/vue";
import App from "@/App.vue";
import components from "@/global/components";
import plugins from "@/global/plugins";
import router from "@/router";
import "wicg-inert";
import "@/global/meta";

/** log env variables for debugging */
console.info(import.meta.env);

/** environment mode */
const mode = import.meta.env.MODE;

/** create main app object */
let app = createApp(App);

/** register plugins/middleware */
for (const [plugin, options] of plugins) app = app.use(plugin, options);

/** register global components */
for (const [name, Component] of Object.entries(components))
  app = app.component(name, Component);

/** track errors with Sentry */
if (mode === "production")
  Sentry.init({
    app,
    dsn: "https://122020f2154c48fa9ebbc53b98afdcf8@o1351894.ingest.sentry.io/6632682",
    integrations: [
      new BrowserTracing({
        routingInstrumentation: Sentry.vueRouterInstrumentation(router),
      }),
    ],
    tracesSampleRate: 1.0,
    logErrors: true,
    environment: mode,
  });

/** hotjar analytics */
app.use(Hotjar, {
  id: "3100256",
  isProduction: mode === "production",
});

/** google analytics */
if (mode === "production")
  app.use(VueGtag, { config: { id: "G-RDNWN51PE8" } }, router);

/** whether to mock api responses, based on env */
const mock: { [key: string]: boolean } = {
  development: true,
  test: true,
  production: false,
};

(async () => {
  /** mock api */
  if (mock[mode]) {
    const { setupWorker } = await import("msw");
    const { handlers } = await import("../fixtures");
    await setupWorker(...handlers).start();
  }

  /** start app */
  app.mount("#app");
})();
