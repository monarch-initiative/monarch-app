import { defineComponent, h } from "vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { mount as vtuMount, type VueWrapper } from "@vue/test-utils";
import SourceAssociationBrowser from "@/components/dashboard/SourceAssociationBrowser.vue";
import components from "@/global/components";
import plugins from "@/global/plugins";
import "@/global/icons";
import { emptyFilters } from "@/composables/use-source-dashboard";

/** mock association results returned by the API */
const mockAssociationResults = {
  items: [
    {
      id: "uuid:1",
      subject: "HGNC:1100",
      subject_label: "BRCA1",
      subject_category: "biolink:Gene",
      predicate: "biolink:has_phenotype",
      object: "HP:0000001",
      object_label: "All",
      object_category: "biolink:PhenotypicFeature",
      negated: false,
      category: "biolink:GeneToPhenotypicFeatureAssociation",
      primary_knowledge_source: "infores:hpo-annotations",
      aggregator_knowledge_source: ["infores:monarchinitiative"],
      provided_by: "hpoa_gene_to_phenotype_edges",
      knowledge_level: "knowledge_assertion",
      agent_type: "manual_agent",
    },
  ],
  total: 1,
  facet_fields: [
    {
      label: "category",
      facet_values: [
        {
          label: "biolink:GeneToPhenotypicFeatureAssociation",
          count: 1,
        },
      ],
    },
    {
      label: "predicate",
      facet_values: [{ label: "biolink:has_phenotype", count: 1 }],
    },
  ],
};

const mockGetSourceAssociations = vi
  .fn()
  .mockResolvedValue(mockAssociationResults);

vi.mock("@/api/source-associations", () => ({
  getSourceAssociations: (...args: unknown[]) =>
    mockGetSourceAssociations(...args),
}));

/** stub components that use import.meta.env (not available in test SSR context) */
const StubComponent = defineComponent({
  props: {
    node: { type: Object, default: () => ({}) },
    association: { type: Object, default: () => ({}) },
  },
  setup(props) {
    return () => h("span", { class: "stub" }, props.node?.name || "stub");
  },
});

const setFilter = vi.fn();
const clearFilters = vi.fn();

const defaultProps = () => ({
  inforesId: "infores:hpo-annotations",
  filters: emptyFilters(),
  filterQueries: [] as string[],
  offset: 0,
  limit: 20,
  hasActiveFilters: false,
  setFilter,
  clearFilters,
});

describe("SourceAssociationBrowser", () => {
  let wrapper: VueWrapper;

  const mountBrowser = async (propsOverride = {}) => {
    const w = vtuMount(SourceAssociationBrowser, {
      props: { ...defaultProps(), ...propsOverride },
      global: {
        components,
        plugins,
        stubs: {
          teleport: true,
          AppNodeBadge: StubComponent,
          AppPredicateBadge: StubComponent,
          AppNodeText: StubComponent,
        },
      },
    });
    // Wait for the async fetchAssociations triggered by immediate watcher
    await vi.runAllTimersAsync();
    await w.vm.$nextTick();
    await w.vm.$nextTick();
    return w;
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    if (wrapper) wrapper.unmount();
    vi.useRealTimers();
  });

  it("renders the filter sidebar", async () => {
    wrapper = await mountBrowser();
    expect(wrapper.find(".filter-sidebar").exists()).toBe(true);
  });

  it("renders the search input", async () => {
    wrapper = await mountBrowser();
    expect(wrapper.find("#filter-search").exists()).toBe(true);
  });

  it("calls the API on mount", async () => {
    wrapper = await mountBrowser();
    expect(mockGetSourceAssociations).toHaveBeenCalled();
  });

  it("passes inforesId to the API call", async () => {
    wrapper = await mountBrowser({ inforesId: "infores:hpo-annotations" });
    expect(mockGetSourceAssociations).toHaveBeenCalledWith(
      "infores:hpo-annotations",
      expect.any(Number),
      expect.any(Number),
      expect.any(Array),
      undefined,
      null,
      undefined,
    );
  });

  it("passes empty inforesId as undefined to the API", async () => {
    wrapper = await mountBrowser({ inforesId: "" });
    expect(mockGetSourceAssociations).toHaveBeenCalledWith(
      undefined,
      expect.any(Number),
      expect.any(Number),
      expect.any(Array),
      undefined,
      null,
      undefined,
    );
  });

  it("shows total count when results load", async () => {
    wrapper = await mountBrowser();
    const totalCount = wrapper.find(".total-count");
    expect(totalCount.exists()).toBe(true);
    expect(totalCount.text()).toContain("1");
  });

  it("does not show clear all when no filters are active", async () => {
    wrapper = await mountBrowser({ hasActiveFilters: false });
    expect(wrapper.find(".clear-all-link").exists()).toBe(false);
  });

  it("shows clear all when filters are active", async () => {
    wrapper = await mountBrowser({ hasActiveFilters: true });
    expect(wrapper.find(".clear-all-link").exists()).toBe(true);
  });

  it("calls clearFilters when clear all is clicked", async () => {
    wrapper = await mountBrowser({ hasActiveFilters: true });
    const clearBtn = wrapper.find(".clear-all-link");
    await clearBtn.trigger("click");
    expect(clearFilters).toHaveBeenCalled();
  });

  it("debounces search input", async () => {
    wrapper = await mountBrowser();

    const input = wrapper.find("#filter-search");
    await input.setValue("BRCA");
    await input.trigger("input");

    // setFilter should not have been called yet (debounce active)
    expect(setFilter).not.toHaveBeenCalledWith("search", "BRCA");

    // advance past debounce timer
    await vi.advanceTimersByTimeAsync(350);
    expect(setFilter).toHaveBeenCalledWith("search", "BRCA");
  });

  it("shows error state when API fails", async () => {
    mockGetSourceAssociations.mockRejectedValueOnce(new Error("API Error"));
    wrapper = await mountBrowser();
    expect(wrapper.text()).toContain("Error");
  });

  it("renders the sidebar toggle button", async () => {
    wrapper = await mountBrowser();
    const toggle = wrapper.find(".sidebar-toggle");
    expect(toggle.exists()).toBe(true);
    expect(toggle.text()).toContain("Hide Filters");
  });

  it("toggles sidebar visibility", async () => {
    wrapper = await mountBrowser();
    const toggle = wrapper.find(".sidebar-toggle");

    // Click toggle to hide
    await toggle.trigger("click");
    expect(toggle.text()).toContain("Show Filters");
  });

  it("omits source facet when scoped to a source", async () => {
    wrapper = await mountBrowser({ inforesId: "infores:hpo-annotations" });
    const headings = wrapper
      .findAll(".facet-heading")
      .map((el: { text: () => string }) => el.text());
    expect(headings).not.toContain("Source");
  });

  it("shows source facet when not scoped to a source", async () => {
    wrapper = await mountBrowser({ inforesId: "" });
    const headings = wrapper
      .findAll(".facet-heading")
      .map((el: { text: () => string }) => el.text());
    expect(headings).toContain("Source");
  });

  it("shows facet values from API response", async () => {
    wrapper = await mountBrowser();
    const facetLinks = wrapper.findAll(".facet-link");
    expect(facetLinks.length).toBeGreaterThan(0);
  });

  it("calls setFilter when a facet value is clicked", async () => {
    wrapper = await mountBrowser();
    const firstFacetLink = wrapper.find(".facet-link");
    if (firstFacetLink.exists()) {
      await firstFacetLink.trigger("click");
      expect(setFilter).toHaveBeenCalled();
    }
  });

  it("shows retry button on error", async () => {
    mockGetSourceAssociations.mockRejectedValueOnce(new Error("API Error"));
    wrapper = await mountBrowser();
    const retryButton = wrapper.find(".retry-button");
    expect(retryButton.exists()).toBe(true);
  });

  it("retries fetch when retry button is clicked", async () => {
    mockGetSourceAssociations.mockRejectedValueOnce(new Error("API Error"));
    wrapper = await mountBrowser();
    mockGetSourceAssociations.mockResolvedValueOnce(mockAssociationResults);

    const retryButton = wrapper.find(".retry-button");
    await retryButton.trigger("click");
    await vi.runAllTimersAsync();
    await wrapper.vm.$nextTick();

    // Should have been called twice: once on mount (failed), once on retry
    expect(mockGetSourceAssociations).toHaveBeenCalledTimes(2);
  });
});
