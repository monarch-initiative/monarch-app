import type {
  NavigationGuard,
  RouteRecordRaw,
  RouterScrollBehavior,
} from "vue-router";
import { createRouter, createWebHistory } from "vue-router";
import { isEmpty, pick } from "lodash";
import { hideAll } from "tippy.js";
import { lookupNode } from "@/api/node-lookup";
import descriptions from "@/router/descriptions.json";
import { sleep } from "@/util/debug";
import { parse } from "@/util/object";
import PageAbout from "@/views/about/PageAbout.vue";
import PageCite from "@/views/about/PageCite.vue";
import PageOverview from "@/views/about/PageOverview.vue";
import PagePublications from "@/views/about/PagePublications.vue";
import PageSources from "@/views/about/PageSources.vue";
import PageTeam from "@/views/about/PageTeam.vue";
import PageTerms from "@/views/about/PageTerms.vue";
import PageExplore from "@/views/explore/PageExplore.vue";
import PageFeedback from "@/views/help/PageFeedback.vue";
import PageHelp from "@/views/help/PageHelp.vue";
import PageNode from "@/views/node/PageNode.vue";
import PageHome from "@/views/PageHome.vue";
import PageTestbed from "@/views/PageTestbed.vue";

/** List of routes and corresponding components. */
/** KEEP IN SYNC WITH PUBLIC/SITEMAP.XML */
export const routes: RouteRecordRaw[] = [
  /** Home page */
  {
    path: "/",
    name: "Home",
    component: PageHome,
    beforeEnter: (async () => {
      /** Look for redirect in session storage (saved from public/404.html page) */
      const redirect = window.sessionStorage.redirect;
      let redirectState = parse(window.sessionStorage.redirectState, {});

      /** After consuming, remove storage values */
      window.sessionStorage.removeItem("redirect");
      window.sessionStorage.removeItem("redirectState");

      /** Log for debugging */
      console.info("Redirecting to:", redirect);
      console.info("With state:", redirectState);

      /**
       * Only keep state added by app, as to not interfere with built-in browser
       * nav
       */
      redirectState = pick(redirectState, ["phenotypes", "breadcrumbs"]);

      /** Apply state to current route */
      if (!isEmpty(redirectState))
        window.history.replaceState(redirectState, "");

      /** Go to appropriate route */
      if (redirect) return redirect;
    }) as NavigationGuard,
  },
  {
    path: "/home",
    redirect: "/",
  },

  /** Top level pages */
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

  /** About pages */
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

  /** Help pages */
  {
    path: "/feedback",
    name: "Feedback",
    component: PageFeedback,
  },

  /** Node pages */
  {
    path: "/:category/:id",
    name: "Node",
    component: PageNode,
  },
  {
    path: "/:id",
    name: "NodeRaw",
    component: PageHome,
    beforeEnter: (async (to) => {
      /** Try to lookup node id and infer category */
      const id = to.path.slice(1) as string;
      if (id) {
        const node = await lookupNode(id);
        return `/${node.category}/${id}`;
      }
    }) as NavigationGuard,
  },

  /** Test pages (comment this out when we release app) */
  {
    path: "/testbed",
    name: "Testbed",
    component: PageTestbed,
  },

  /** If no other route match found (404) */
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: PageHome,
  },
];

/** Merge in route descriptions */
routes.forEach(
  (route) =>
    (route.meta = {
      description:
        (descriptions as { [key: string]: string })[String(route.name || "")] ||
        import.meta.env.VITE_DESCRIPTION,
    })
);

/** Vue-router's scroll behavior handler */
const scrollBehavior: RouterScrollBehavior = async (
  to,
  from,
  savedPosition
) => {
  /** https://github.com/vuejs/vue-router-next/issues/1147 */
  await sleep();

  /** Scroll to previous position if exists */
  if (savedPosition) return savedPosition;

  /** Scroll to element corresponding to hash */
  const element = document?.getElementById(to.hash.slice(1));
  if (element)
    return { el: getTarget(element), top: getOffset(), behavior: "smooth" };

  /** Otherwise don't change scroll */
};

/** Given element, get (possibly) modified target */
const getTarget = (element: Element): Element => {
  /** Move target to parent section element if first child */
  if (
    element.parentElement?.tagName === "SECTION" &&
    element.matches(":first-child")
  )
    return element.parentElement;

  /** Move target to previous horizontal rule */
  if (
    element.previousElementSibling instanceof HTMLElement &&
    element.previousElementSibling?.tagName === "HR"
  )
    return element.previousElementSibling;

  return element;
};

/** Get offset to account for header */
const getOffset = () => document?.querySelector("header")?.clientHeight || 0;

/** Scroll to element */
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

/** Scroll to hash */
export const scrollToHash = () =>
  scrollToElement(document?.getElementById(window.location.hash.slice(1)));

/** Navigation history object */
export const history = createWebHistory(import.meta.env.BASE_URL);

/** Router object */
const router = createRouter({
  history,
  routes,
  scrollBehavior,
});

/** Close any open tooltips on route change */
router.beforeEach(() => {
  hideAll();
});

export default router;
