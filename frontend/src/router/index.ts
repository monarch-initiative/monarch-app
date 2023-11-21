import {
  defineAsyncComponent,
  defineComponent,
  h,
  type AsyncComponentLoader,
} from "vue";
import type { RouteRecordRaw, RouterScrollBehavior } from "vue-router";
import { createRouter, createWebHistory } from "vue-router";
import { isEmpty, pick } from "lodash";
import { hideAll } from "tippy.js";
import AppPlaceholder from "@/components/AppPlaceholder.vue";
import descriptions from "@/router/descriptions.json";
import { sleep } from "@/util/debug";
import { waitFor } from "@/util/dom";
import { parse } from "@/util/object";

/**
 * generate async loaded route. normal lazy loaded route renders homepage/root
 * route as loading fallback, this allows any loading fallback.
 */
const asyncRoute = (loader: AsyncComponentLoader) =>
  /** https://stackoverflow.com/questions/67044999 */
  defineComponent({
    render() {
      const component = defineAsyncComponent({
        loader,
        loadingComponent: AppPlaceholder,
      });
      return h(component);
    },
  });

/** list of routes and corresponding components. */
/** KEEP IN SYNC WITH PUBLIC/SITEMAP.XML */
export const routes: RouteRecordRaw[] = [
  /** home page */
  {
    path: "/",
    name: "Home",
    component: asyncRoute(() => import("../pages/PageHome.vue")),
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
        console.info("Redirecting to:", redirect);
        console.info("With state:", state);
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
  },

  /** top level pages */
  {
    path: "/explore",
    name: "Explore",
    component: asyncRoute(() => import("../pages/explore/PageExplore.vue")),
  },
  {
    path: "/about",
    name: "About",
    component: asyncRoute(() => import("../pages/about/PageAbout.vue")),
  },
  {
    path: "/help",
    name: "Help",
    component: asyncRoute(() => import("../pages/help/PageHelp.vue")),
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
    component: asyncRoute(() => import("../pages/about/PageCite.vue")),
  },
  {
    path: "/team",
    name: "Team",
    component: asyncRoute(() => import("../pages/about/PageTeam.vue")),
  },
  {
    path: "/publications",
    name: "Publications",
    component: asyncRoute(() => import("../pages/about/PagePublications.vue")),
  },
  {
    path: "/terms",
    name: "Terms",
    component: asyncRoute(() => import("../pages/about/PageTerms.vue")),
  },
  {
    path: "/phenomics-first",
    name: "PhenomicsFirst",
    component: asyncRoute(
      () => import("../pages/about/PagePhenomicsFirst.vue"),
    ),
  },
  {
    path: "/outreach",
    name: "Outreach",
    component: asyncRoute(() => import("../pages/about/PageOutreach.vue")),
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
    component: asyncRoute(() => import("../pages/help/PageFeedback.vue")),
  },

  /** node pages */
  {
    path: "/:id",
    name: "Node",
    component: asyncRoute(() => import("../pages/node/PageNode.vue")),
  },

  /** phenogrid iframe widget page */
  {
    path: "/phenogrid",
    name: "Phenogrid",
    component: asyncRoute(() => import("../pages/explore/PagePhenogrid.vue")),
    meta: { bare: true },
  },

  /** test pages (comment this out when we release app) */
  {
    path: "/testbed",
    name: "Testbed",
    component: asyncRoute(() => import("../pages/PageTestbed.vue")),
  },

  /** if no other route match found (404) */
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: asyncRoute(() => import("../pages/PageHome.vue")),
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
