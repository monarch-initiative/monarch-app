import { computed, defineComponent, h, reactive, ref } from "vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { mount, type VueWrapper } from "@vue/test-utils";
import components from "@/global/components";
import plugins from "@/global/plugins";
import PageSourceDashboard from "@/pages/knowledgeGraph/PageSourceDashboard.vue";
import "@/global/icons";

const mockSetFilter = vi.fn();
const mockClearFilters = vi.fn();

vi.mock("@/composables/use-source-dashboard", async () => {
  const actual = await vi.importActual("@/composables/use-source-dashboard");
  return {
    ...actual,
    useSourceDashboard: () => ({
      inforesId: computed(() => "infores:hpo-annotations"),
      sourceName: computed(() => "HPO Annotations"),
      filters: reactive((actual as any).emptyFilters()),
      filterQueries: computed(() => []),
      offset: ref(0),
      limit: ref(20),
      setFilter: mockSetFilter,
      clearFilters: mockClearFilters,
      hasActiveFilters: computed(() => false),
    }),
  };
});

vi.mock("vue-router", () => ({
  useRoute: () => ({
    params: { infores: "hpo-annotations" },
    path: "/kg/source/hpo-annotations",
    meta: {},
  }),
  useRouter: () => ({
    push: vi.fn(),
    resolve: vi.fn(() => ({ href: "/" })),
    options: { routes: [] },
  }),
}));

/** Stub heavy child components */
const StubComponent = defineComponent({
  props: {
    inforesId: { type: String, default: "" },
    sourceName: { type: String, default: "" },
  },
  setup() {
    return () => h("div", { class: "stub" });
  },
});

describe("PageSourceDashboard", () => {
  let wrapper: VueWrapper;

  const mountPage = () => {
    return mount(PageSourceDashboard, {
      global: {
        components,
        plugins,
        stubs: {
          teleport: true,
          AppBreadcrumb: { template: "<div />" },
          PageTitle: defineComponent({
            props: ["title", "id"],
            setup(props) {
              return () => h("h1", {}, props.title);
            },
          }),
          KGDashboard: defineComponent({
            props: ["showDataSourceInfo"],
            setup(_, { slots }) {
              return () =>
                h("div", { class: "stub-kg-dashboard" }, slots.default?.());
            },
          }),
          DataSource: { template: "<div />" },
          SourceCharts: StubComponent,
          SourceAssociationBrowser: StubComponent,
        },
      },
    });
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    if (wrapper) wrapper.unmount();
  });

  it("renders sourceName as title", () => {
    wrapper = mountPage();
    expect(wrapper.text()).toContain("HPO Annotations");
  });

  it("renders inforesId link", () => {
    wrapper = mountPage();
    expect(wrapper.text()).toContain("infores:hpo-annotations");
  });

  it("onFilterPredicate calls setFilter with predicate", async () => {
    wrapper = mountPage();
    // Access the component's onFilterPredicate function
    (wrapper.vm as any).onFilterPredicate("biolink:has_phenotype");
    expect(mockSetFilter).toHaveBeenCalledWith(
      "predicate",
      "biolink:has_phenotype",
    );
  });

  it("onFilterCategory calls setFilter with category type", async () => {
    wrapper = mountPage();
    (wrapper.vm as any).onFilterCategory("biolink:Gene", "subjectCategory");
    expect(mockSetFilter).toHaveBeenCalledWith(
      "subjectCategory",
      "biolink:Gene",
    );
  });
});
