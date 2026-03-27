import { defineComponent, h } from "vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { mount, type VueWrapper } from "@vue/test-utils";
import components from "@/global/components";
import plugins from "@/global/plugins";
import PageAssociationBrowser from "@/pages/knowledgeGraph/PageAssociationBrowser.vue";
import "@/global/icons";

vi.mock("vue-router", () => ({
  useRoute: () => ({
    params: {},
    path: "/kg/associations",
    meta: {},
  }),
  useRouter: () => ({
    push: vi.fn(),
    resolve: vi.fn(() => ({ href: "/" })),
    options: { routes: [] },
  }),
}));

vi.mock("@/api/source-associations", () => ({
  getSourceAssociations: vi.fn().mockResolvedValue({
    items: [],
    total: 0,
    facet_fields: [],
  }),
}));

describe("PageAssociationBrowser", () => {
  let wrapper: VueWrapper;

  const mountPage = () => {
    return mount(PageAssociationBrowser, {
      global: {
        components,
        plugins,
        stubs: {
          teleport: true,
          AppBreadcrumb: { template: "<div />" },
          PageTitle: defineComponent({
            props: ["title", "id"],
            setup(props) {
              return () => h("h1", { class: "page-title" }, props.title);
            },
          }),
          SourceAssociationBrowser: defineComponent({
            props: [
              "filters",
              "filterQueries",
              "offset",
              "limit",
              "hasActiveFilters",
              "setFilter",
              "clearFilters",
            ],
            setup() {
              return () => h("div", { class: "stub-browser" });
            },
          }),
        },
      },
    });
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    if (wrapper) wrapper.unmount();
    vi.useRealTimers();
  });

  it("renders page title", () => {
    wrapper = mountPage();
    expect(wrapper.text()).toContain("Association Browser");
  });

  it("renders description text", () => {
    wrapper = mountPage();
    expect(wrapper.text()).toContain(
      "Browse and filter all associations in the Monarch Knowledge Graph",
    );
  });

  it("renders SourceAssociationBrowser stub", () => {
    wrapper = mountPage();
    expect(wrapper.find(".stub-browser").exists()).toBe(true);
  });
});
