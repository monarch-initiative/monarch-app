import { expect, test, vi } from "vitest";
import { mount } from "@vue/test-utils";
import TabSearch from "@/components/TabSearch.vue";
import components from "@/global/components";
import plugins from "@/global/plugins";
import PageSearchResults from "@/pages/knowledgeGraph/PageSearchResults.vue";
import "@/global/icons";
import { apiCall } from "./setup";

vi.mock("vue-router", () => ({
  useRoute: () => ({
    params: {},
    path: "/results",
    query: {},
    meta: {},
    /** AppBreadcrumb walks this */
    matched: [],
  }),
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    resolve: vi.fn(() => ({ href: "/" })),
    options: { routes: [] },
  }),
}));

const mountPage = () =>
  mount(PageSearchResults, {
    global: { components, plugins, stubs: { teleport: true } },
  });

/**
 * This page was once a ~500 line fork of TabSearch. The two drifted, and a fix
 * to TabSearch's facet options had no effect because nothing rendered them:
 * TabSearch is used elsewhere only with minimal=true, where that markup is
 * gated off. These two assertions fail if the page is forked again, or if it
 * ever renders TabSearch in the wrong mode.
 */
test("Delegates to TabSearch rather than reimplementing it", () => {
  expect(mountPage().findComponent(TabSearch).exists()).toBe(true);
});

test("Renders TabSearch's full (non-minimal) mode", () => {
  /** only present when minimal is falsy, so it pins the branch the page needs */
  expect(mountPage().find(".search-row-full").exists()).toBe(true);
});

test("Lists page buttons in numeric order", async () => {
  const wrapper = mountPage();
  await apiCall();
  const pages = wrapper.findAll(".page-button").map((b) => Number(b.text()));
  /** search fixture has 134 results; at 10 per page that's 14 pages */
  expect(pages).toEqual([1, 2, 3, 12, 13, 14]);
});
