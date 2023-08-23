import type { RouteRecordRaw, RouterScrollBehavior } from "vue-router";
import { createRouter, createWebHistory } from "vue-router";
import { isEmpty, pick } from "lodash";
import { hideAll } from "tippy.js";
import PageAbout from "@/pages/about/PageAbout.vue";
import PageCite from "@/pages/about/PageCite.vue";
import PageOverview from "@/pages/about/PageOverview.vue";
import PagePhenomicsFirst from "@/pages/about/PagePhenomicsFirst.vue";
import PagePublications from "@/pages/about/PagePublications.vue";
import PageTeam from "@/pages/about/PageTeam.vue";
import PageTerms from "@/pages/about/PageTerms.vue";
import PageExplore from "@/pages/explore/PageExplore.vue";
import PageFeedback from "@/pages/help/PageFeedback.vue";
import PageHelp from "@/pages/help/PageHelp.vue";
import PageNode from "@/pages/node/PageNode.vue";
import PageHome from "@/pages/PageHome.vue";
import PageTestbed from "@/pages/PageTestbed.vue";
import descriptions from "@/router/descriptions.json";
import { sleep } from "@/util/debug";
import { parse } from "@/util/object";

/** list of routes and corresponding components. */
/** KEEP IN SYNC WITH PUBLIC/SITEMAP.XML */
export const routes: RouteRecordRaw[] = [
  /** home page */
  {
    path: "/",
    name: "Home",
    component: PageHome,
    beforeEnter: async () => {
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
    component: PageExplore,
  },
  {
    path: "/about",
    name: "About",
    component: PageAbout,
  },
  {
    path: "/help",
    name: "Help",
    component: PageHelp,
  },

  /** about pages */
  {
    path: "/overview",
    name: "Overview",
    component: PageOverview,
  },
  {
    path: "/cite",
    name: "Cite",
    component: PageCite,
  },
  {
    path: "/team",
    name: "Team",
    component: PageTeam,
  },
  {
    path: "/publications",
    name: "Publications",
    component: PagePublications,
  },
  {
    path: "/terms",
    name: "Terms",
    component: PageTerms,
  },
  {
    path: "/phenomics-first",
    name: "PhenomicsFirst",
    component: PagePhenomicsFirst,
  },

  /** help pages */
  {
    path: "/feedback",
    name: "Feedback",
    component: PageFeedback,
  },

  /** node pages */
  {
    path: "/node/:id",
    name: "Node",
    component: PageNode,
  },

  /** test pages (comment this out when we release app) */
  {
    path: "/testbed",
    name: "Testbed",
    component: PageTestbed,
  },

  /** if no other route match found (404) */
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: PageHome,
  },
];

/** insert descriptions from imported json into each route's metadata */
for (const route of routes)
  route.meta = {
    description:
      (descriptions as { [key: string]: string })[String(route.name || "")] ||
      import.meta.env.VITE_DESCRIPTION,
  };

/** vue-router's scroll behavior handler */
const scrollBehavior: RouterScrollBehavior = async (
  to,
  from,
  savedPosition,
) => {
  /** https://github.com/vuejs/vue-router-next/issues/1147 */
  await sleep();

  /** scroll to previous position if exists */
  if (savedPosition) return savedPosition;

  /** scroll to element corresponding to hash */
  const element = document?.getElementById(to.hash.slice(1));
  if (element)
    return { el: getTarget(element), top: getOffset(), behavior: "smooth" };

  /** otherwise don't change scroll */
};

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

/** get offset to account for header */
const getOffset = () => document?.querySelector("header")?.clientHeight || 0;

/** scroll to element */
export const scrollToElement = async (element?: Element | null) => {
  if (!element) return;

  window.scrollTo({
    top:
      getTarget(element).getBoundingClientRect().top +
      window.scrollY -
      getOffset(),
    behavior: "smooth",
  });
};

/** scroll to hash */
export const scrollToHash = () =>
  scrollToElement(document?.getElementById(window.location.hash.slice(1)));

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

export default router;
