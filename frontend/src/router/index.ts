import {
  createRouter,
  createWebHistory,
  RouteRecordRaw,
  RouterScrollBehavior,
  NavigationGuard,
} from "vue-router";
import { isEmpty, pick } from "lodash";
import { hideAll } from "tippy.js";
import PageHome from "@/views/PageHome.vue";
import PageExplore from "@/views/explore/PageExplore.vue";
import PageAbout from "@/views/about/PageAbout.vue";
import PageOverview from "@/views/about/PageOverview.vue";
import PageSources from "@/views/about/PageSources.vue";
import PageCite from "@/views/about/PageCite.vue";
import PageTeam from "@/views/about/PageTeam.vue";
import PagePublications from "@/views/about/PagePublications.vue";
import PageTerms from "@/views/about/PageTerms.vue";
import PageHelp from "@/views/help/PageHelp.vue";
import PageFeedback from "@/views/help/PageFeedback.vue";
import PageNode from "@/views/node/PageNode.vue";
import PageTestbed from "@/views/PageTestbed.vue";
import { sleep } from "@/util/debug";
import { parse } from "@/util/object";
import descriptions from "@/router/descriptions.json";

/** list of routes and corresponding components. */
/** KEEP IN SYNC WITH PUBLIC/SITEMAP.XML */
export const routes: Array<RouteRecordRaw> = [
  /** home page */
  {
    path: "/",
    name: "Home",
    component: PageHome,
    beforeEnter: (async () => {
      /** look for redirect in session storage (saved from public/404.html page) */
      const redirect = window.sessionStorage.redirect;
      let redirectState = parse(window.sessionStorage.redirectState, {});

      /** after consuming, remove storage values */
      window.sessionStorage.removeItem("redirect");
      window.sessionStorage.removeItem("redirectState");

      /** log for debugging */
      console.info("Redirecting to:", redirect);
      console.info("With state:", redirectState);

      /**
       * only keep state added by app, as to not interfere with built-in browser
       * nav
       */
      redirectState = pick(redirectState, ["phenotypes", "breadcrumbs"]);

      /** apply state to current route */
      if (!isEmpty(redirectState))
        window.history.replaceState(redirectState, "");

      /** go to appropriate route */
      if (redirect) return redirect;
    }) as NavigationGuard,
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
    path: "/sources",
    name: "Sources",
    component: PageSources,
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
  {
    path: "/:id",
    name: "NodeRaw",
    component: PageHome,
    beforeEnter: (async (to) => {
      /** try to lookup node id and infer category */
      const id = to.path.slice(1) as string;
      if (id) {
        return `/node/${id}`;
      }
    }) as NavigationGuard,
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

/** merge in route descriptions */
routes.forEach(
  (route) =>
    (route.meta = {
      description:
        (descriptions as Record<string, string>)[String(route.name || "")] ||
        process.env.VUE_APP_DESCRIPTION,
    })
);

/** vue-router's scroll behavior handler */
const scrollBehavior: RouterScrollBehavior = async (
  to,
  from,
  savedPosition
) => {
  /** https://github.com/vuejs/vue-router-next/issues/1147 */
  await sleep();

  /** scroll to previous position if exists */
  if (savedPosition) return savedPosition;

  /** scroll to element corresponding to hash */
  const element = document?.getElementById(to.hash.slice(1));
  if (element)
    return { el: getTarget(element), top: getOffset(), behavior: "smooth" };

  /** otherwise just scroll to top */
  return { top: 0, left: 0 };
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
export const history = createWebHistory(process.env.BASE_URL);

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
