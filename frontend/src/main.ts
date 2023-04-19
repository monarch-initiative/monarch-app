import { createApp } from "vue";
import * as Sentry from "@sentry/vue";
import { BrowserTracing } from "@sentry/tracing";
import VueGtag from "vue-gtag";
import Hotjar from "vue-hotjar";
import "wicg-inert";
import App from "@/App.vue";
import components from "@/global/components";
import plugins from "@/global/plugins";
import router from "@/router";
import "@/global/meta";

/** log env variables for debugging */
console.info(import.meta.env);

/** create main app object */
let app = createApp(App);

/** register plugins/middleware */
for (const [plugin, options] of plugins) app = app.use(plugin, options);

/** register global components */
for (const [name, Component] of Object.entries(components))
  app = app.component(name, Component);

/** track errors with Sentry */
if (import.meta.env.NODE_ENV === "production")
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
    environment: import.meta.env.NODE_ENV,
  });

/** hotjar analytics */
app.use(Hotjar, {
  id: "3100256",
  isProduction: import.meta.env.NODE_ENV === "production",
});

/** google analytics */
if (import.meta.env.NODE_ENV === "production")
  app.use(VueGtag, { config: { id: "G-RDNWN51PE8" } }, router);

(async () => {
  /** mock api for local development */
  // const { setupWorker } = await import("msw");
  // const { handlers } = await import("../tests/fixtures");
  // await setupWorker(...handlers).start();

  /** start app */
  app.mount("#app");
})();
