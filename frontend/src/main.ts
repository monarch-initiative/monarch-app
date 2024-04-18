import { createApp } from "vue";
import VueGtag from "vue-gtag";
import Hotjar from "vue-hotjar";
import * as Sentry from "@sentry/vue";
import App from "@/App.vue";
import components from "@/global/components";
import plugins from "@/global/plugins";
import router from "@/router";
import "@/global/icons";
import "@/global/meta";
import "normalize.css";
import "@/global/styles.scss"; /** keep these last so they take priority */

console.debug("Env variables", import.meta.env);

/** create main app object */
export let app = createApp(App);

/** register plugins/middleware */
for (const [plugin, options] of plugins) app = app.use(plugin, options);

/** register global components */
for (const [name, Component] of Object.entries(components))
  app = app.component(name, Component);

/** init analytics, if on publicly deployed instance of frontend */
if (new URL(window.location.href).hostname.endsWith("monarchinitiative.org")) {
  /** track errors with Sentry */
  Sentry.init({
    app,
    dsn: "https://122020f2154c48fa9ebbc53b98afdcf8@o1351894.ingest.sentry.io/6632682",
    integrations: [
      Sentry.browserTracingIntegration({ router }),
      Sentry.replayIntegration(),
    ],
    tracesSampleRate: 1.0,
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
  });

  /** hotjar analytics */
  app.use(Hotjar, { id: "3100256" });

  /** google analytics */
  app.use(VueGtag, { config: { id: "G-TWM5ED4QJB" } }, router);
}

(async () => {
  /** mock api */
  if (
    import.meta.env.MODE === "test" ||
    import.meta.env.VITE_MOCK === "true" ||
    new URL(
      window.sessionStorage.redirect || window.location.href,
    ).searchParams.get("mock") === "true"
  ) {
    const { setupWorker } = await import("msw/browser");
    const { handlers } = await import("../fixtures");
    await setupWorker(...handlers).start();
  }

  /** start app */
  app.mount("#app");
})();
