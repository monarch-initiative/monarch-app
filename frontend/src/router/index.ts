import { defineAsyncComponent, defineComponent, h, type Component } from "vue";
import type { RouteRecordRaw, RouterScrollBehavior } from "vue-router";
import { createRouter, createWebHistory } from "vue-router";
import { isEmpty, pick } from "lodash";
import { hideAll } from "tippy.js";
import AppPlaceholder from "@/components/AppPlaceholder.vue";
import { initRouter } from "@/composables/use-param";
import descriptions from "@/router/descriptions.json";
import { sleep } from "@/util/debug";
import { waitFor } from "@/util/dom";
import { parse } from "@/util/object";

/**
 * generate async loaded route. normal lazy loaded route renders homepage/root
 * route as loading fallback, this allows any loading fallback.
 * https://stackoverflow.com/questions/67044999/how-to-use-createasynccomponent-in-vuerouter4-0-0-vue3/77629317#77629317
 */
const asyncRoute = (path: string) => {
  const component = defineAsyncComponent({
    loader: () =>
      import.meta
        .glob<false, string, Component>("../pages/**/*.vue")
        [`../pages/${path}.vue`](),
    loadingComponent: AppPlaceholder,
  });
  return defineComponent({ render: () => h(component) });
};

/** list of routes and corresponding components. */
/** KEEP IN SYNC WITH PUBLIC/SITEMAP.XML */
export const routes: RouteRecordRaw[] = [
  /** home page */
  {
    path: "/",
    name: "Home",
    component: asyncRoute("PageHome"),
    meta: { breadcrumb: "Home" },
    beforeEnter: () => {
      /** look for redirect in session storage (saved from public/404.html page) */
      const redirect = window.sessionStorage.redirect || "";
      const redirectState = window.sessionStorage.redirectState || "{}";

      /** parse serialized state */
      const state = pick(
        parse<{ [key: string]: unknown }>(redirectState, {}),
        /** only keep fields added by this app */
        ["phenotypes", "breadcrumbs", "fromSearch"],
      );

      /** after consuming, remove storage values */
      window.sessionStorage.removeItem("redirect");
      window.sessionStorage.removeItem("redirectState");

      if (import.meta.env.MODE !== "test") {
        console.debug("Redirecting to:", redirect);
        console.debug("With state:", state);
      }

      /** apply state to current route */
      if (!isEmpty(state)) window.history.replaceState(state, "");

      /** go to appropriate route */
      if (redirect) {
        const { pathname, search, hash } = new URL(redirect);
        return pathname + search + hash;
      }
    },
  },
  {
    path: "/home",
    redirect: "/",
    meta: { breadcrumb: "Home" },
  },

  /** top level pages */
  {
    path: "/explore",
    name: "Explore",
    component: asyncRoute("explore/PageExplore"),
  },
  {
    path: "/about",
    name: "About",
    component: asyncRoute("about/PageAbout"),
  },
  {
    path: "/help",
    name: "Help",
    component: asyncRoute("help/PageHelp"),
  },

  /** about pages */
  {
    path: "/overview",
    name: "Overview",
    component: () => import("../pages/about/PageOverview.vue"),
  },
  {
    path: "/cite",
    name: "Cite",
    component: asyncRoute("about/PageCite"),
  },
  {
    path: "/team",
    name: "Team",
    component: asyncRoute("about/PageTeam"),
  },
  {
    path: "/publications",
    name: "Publications",
    component: asyncRoute("about/PagePublications"),
  },
  {
    path: "/terms",
    name: "Terms",
    component: asyncRoute("about/PageTerms"),
  },
  {
    path: "/phenomics-first",
    name: "PhenomicsFirst",
    component: asyncRoute("about/PagePhenomicsFirst"),
  },
  {
    path: "/outreach",
    name: "Outreach",
    component: asyncRoute("about/PageOutreach"),
  },
  {
    path: "/how-to",
    name: "HowTo",
    component: asyncRoute("about/PageHowTo"),
  },

  /** resources page */
  {
    path: "/resources",
    name: "Resources",
    component: () => import("../pages/resources/PageResources.vue"),
  },

  /** help pages */
  {
    path: "/feedback",
    name: "Feedback",
    component: asyncRoute("help/PageFeedback"),
  },

  /** node pages */
  {
    path: "/:id",
    name: "Node",
    component: asyncRoute("node/PageNode"),
  },

  /** phenogrid compare iframe widget page */
  {
    path: "/phenogrid-search",
    name: "Phenogrid",
    component: asyncRoute("explore/PagePhenogridSearch"),
    meta: { bare: true },
  },

  /** phenogrid multi-compare iframe widget page */
  {
    path: "/phenogrid-multi-compare",
    name: "PhenogridMultiCompare",
    component: asyncRoute("explore/PagePhenogridMulticompare"),
    meta: { bare: true },
  },

  /** test pages (comment this out when we release app) */
  {
    path: "/testbed",
    name: "Testbed",
    component: asyncRoute("PageTestbed"),
  },

  /** if no other route match found (404) */
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: asyncRoute("PageHome"),
  },

  {
    path: "/kg/about",
    name: "KnowledgeGraphAbout",
    component: asyncRoute("knowledgeGraph/PageAbout"),
    meta: { breadcrumb: "About KG" },
  },
  {
    path: "/kg/citation",
    name: "KnowledgeGraphCite",
    component: asyncRoute("knowledgeGraph/PageCite"),
    meta: { breadcrumb: "Citation" },
  },
  {
    path: "/kg/help",
    name: "KnowledgeGraphHelp",
    component: asyncRoute("knowledgeGraph/PageHelp"),
    meta: { breadcrumb: "How to & Help" },
  },
  {
    path: "/kg/status",
    name: "KnowldgeGraphStatusQc",
    component: asyncRoute("knowledgeGraph/PageStatus"),
    meta: { breadcrumb: "Status & QC" },
  },
  {
    path: "/kg",
    name: "KnowledgeGraph",
    component: asyncRoute("knowledgeGraph/PageSearch"),
    meta: { breadcrumb: "Search" },
  },
  {
    path: "/kg/results",
    name: "KnowledgeGraphResults",
    component: asyncRoute("knowledgeGraph/PageResults"),
    meta: { breadcrumb: "Search Results" },
  },
  {
    path: "/kg/documentation",
    name: "KnowledgeGraphDocumentation",
    component: asyncRoute("knowledgeGraph/PageDocumentation"),
    meta: { breadcrumb: "Documentation" },
  },
  {
    path: "/kg/terms",
    name: "KnowledgeGraphTerms",
    component: asyncRoute("knowledgeGraph/PageTerms"),
    meta: { breadcrumb: "Terms of Use" },
  },
];

/** insert descriptions from imported json into each route's metadata */
for (const route of routes) {
  route.meta ??= {};
  route.meta.description =
    (descriptions as { [key: string]: string })[String(route.name || "")] ||
    import.meta.env.VITE_DESCRIPTION;
}

/** vue-router's scroll behavior handler */
const scrollBehavior: RouterScrollBehavior = async () => {};

/** given element, get (possibly) modified target */
const getTarget = (element: Element): Element => {
  /** move target to parent section element if first child */
  if (
    element.parentElement?.tagName === "SECTION" &&
    element.matches(":first-child")
  )
    return element.parentElement;

  /** move target to previous horizontal rule */
  if (
    element.previousElementSibling instanceof HTMLElement &&
    element.previousElementSibling?.tagName === "HR"
  )
    return element.previousElementSibling;

  return element;
};

/** scroll to element by selector */
export const scrollTo = async (selector: string) => {
  /** wait for element to appear */
  const element = await waitFor(selector);

  /** wait for layout shifts */
  await sleep(100);

  if (!element) return;

  /** get height of header */
  let offset = 0;
  const header = document.querySelector("header");
  if (header && window.getComputedStyle(header).position === "sticky")
    offset = header.clientHeight;

  /** scroll to element */
  window.scrollTo({
    top:
      getTarget(element).getBoundingClientRect().top + window.scrollY - offset,
    behavior: "smooth",
  });
};

/** navigation history object */
export const history = createWebHistory(import.meta.env.BASE_URL);

/** router object */
const router = createRouter({
  history,
  routes,
  scrollBehavior,
});

/** hook up use-param composable to router */
initRouter(router);

/** close any open tooltips on route change */
router.beforeEach(() => {
  hideAll();
});

/** on route load */
router.afterEach(async ({ hash }) => {
  if (!hash.trim()) return;
  /** scroll to section once it appears */
  scrollTo(hash);
});

export default router;
