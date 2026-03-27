import { defineComponent, h } from "vue";
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
  type Mock,
} from "vitest";
import { flushPromises, mount, type VueWrapper } from "@vue/test-utils";
import SourceCharts from "@/components/dashboard/SourceCharts.vue";
import components from "@/global/components";
import plugins from "@/global/plugins";
import "@/global/icons";

/** Minimal stubs for child chart/card components */
const StubKGMetricCard = defineComponent({
  name: "KGMetricCard",
  props: ["title", "dataSource", "sql", "subtitle"],
  setup(props) {
    return () => h("div", { class: "stub-metric-card" }, props.title);
  },
});

const StubChordChart = defineComponent({
  name: "ChordChart",
  props: [
    "title",
    "dataSource",
    "sql",
    "showControls",
    "allowExport",
    "height",
  ],
  setup() {
    return () => h("div", { class: "stub-chord-chart" });
  },
});

const StubPredicateTable = defineComponent({
  name: "PredicateTable",
  props: ["dataSource", "sql"],
  emits: ["predicate-selected"],
  setup(_, { emit }) {
    return () =>
      h("div", {
        class: "stub-predicate-table",
        onClick: () => emit("predicate-selected", "has_phenotype"),
      });
  },
});

const StubSankeyChart = defineComponent({
  name: "SankeyChart",
  props: [
    "title",
    "dataSource",
    "sql",
    "showControls",
    "allowExport",
    "height",
  ],
  setup() {
    return () => h("div", { class: "stub-sankey-chart" });
  },
});

describe("SourceCharts", () => {
  let wrapper: VueWrapper;
  let mockExecuteQuery: Mock;

  const mountCharts = async (
    executeQuery?: Mock,
    propsOverride: Record<string, unknown> = {},
  ) => {
    mockExecuteQuery = executeQuery ?? vi.fn().mockResolvedValue([]);
    const w = mount(SourceCharts, {
      props: {
        inforesId: "infores:hpo-annotations",
        sourceName: "HPO Annotations",
        ...propsOverride,
      },
      global: {
        components,
        plugins,
        stubs: {
          KGMetricCard: StubKGMetricCard,
          ChordChart: StubChordChart,
          PredicateTable: StubPredicateTable,
          SankeyChart: StubSankeyChart,
        },
        provide: {
          "kg-data": { executeQuery: mockExecuteQuery },
        },
      },
    });
    await flushPromises();
    await w.vm.$nextTick();
    return w;
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    if (wrapper) wrapper.unmount();
  });

  describe("probing state", () => {
    it("renders probing message while probe is pending", () => {
      // Create a never-resolving promise to keep probing=true
      const neverResolve = vi.fn().mockReturnValue(new Promise(() => {}));
      wrapper = mount(SourceCharts, {
        props: {
          inforesId: "infores:hpo-annotations",
          sourceName: "HPO Annotations",
        },
        global: {
          components,
          plugins,
          stubs: {
            KGMetricCard: StubKGMetricCard,
            ChordChart: StubChordChart,
            PredicateTable: StubPredicateTable,
            SankeyChart: StubSankeyChart,
          },
          provide: {
            "kg-data": { executeQuery: neverResolve },
          },
        },
      });
      expect(wrapper.text()).toContain("Analyzing source data complexity");
    });
  });

  describe("column missing errors", () => {
    it("shows warning when error contains 'primary_knowledge_source' and 'not found'", async () => {
      const failQuery = vi
        .fn()
        .mockRejectedValue(
          new Error(
            "Column primary_knowledge_source not found in table edge_report",
          ),
        );
      wrapper = await mountCharts(failQuery);
      expect(wrapper.text()).toContain("does not yet include per-source");
    });

    it("shows warning when error contains 'Binder Error'", async () => {
      const failQuery = vi
        .fn()
        .mockRejectedValue(
          new Error(
            "Binder Error: column primary_knowledge_source does not exist",
          ),
        );
      wrapper = await mountCharts(failQuery);
      expect(wrapper.text()).toContain("does not yet include per-source");
    });

    it("shows warning for generic probe errors", async () => {
      const failQuery = vi
        .fn()
        .mockRejectedValue(new Error("Some other database error"));
      wrapper = await mountCharts(failQuery);
      expect(wrapper.text()).toContain("does not yet include per-source");
    });
  });

  describe("no kgData injected", () => {
    it("finishes probing immediately when no kgData provided", async () => {
      wrapper = mount(SourceCharts, {
        props: {
          inforesId: "infores:hpo-annotations",
          sourceName: "HPO Annotations",
        },
        global: {
          components,
          plugins,
          stubs: {
            KGMetricCard: StubKGMetricCard,
            ChordChart: StubChordChart,
            PredicateTable: StubPredicateTable,
            SankeyChart: StubSankeyChart,
          },
          // No kg-data provide
        },
      });
      await flushPromises();
      await wrapper.vm.$nextTick();
      // No tier set, no probing, no columnMissing → empty component
      expect(wrapper.text()).not.toContain("Analyzing");
      expect(wrapper.text()).not.toContain("does not yet include");
    });
  });

  describe("tier classification", () => {
    it("sets tier to 'simple' when results are empty", async () => {
      wrapper = await mountCharts(vi.fn().mockResolvedValue([]));
      // Simple tier renders metric cards
      expect(wrapper.findAll(".stub-metric-card").length).toBe(4);
    });

    it("sets tier to 'simple' when counts are low", async () => {
      const eq = vi
        .fn()
        .mockResolvedValueOnce([{ sc: 2, oc: 1, p: 2 }])
        .mockResolvedValue([]);
      wrapper = await mountCharts(eq);
      expect(wrapper.findAll(".stub-metric-card").length).toBe(4);
      expect(wrapper.find(".stub-sankey-chart").exists()).toBe(false);
    });

    it("sets tier to 'moderate' when counts are moderate", async () => {
      const eq = vi
        .fn()
        .mockResolvedValueOnce([{ sc: 4, oc: 4, p: 8 }])
        .mockResolvedValue([]);
      wrapper = await mountCharts(eq);
      expect(wrapper.findAll(".stub-metric-card").length).toBe(4);
      expect(wrapper.find(".stub-sankey-chart").exists()).toBe(false);
    });

    it("sets tier to 'complex' when counts are high", async () => {
      const eq = vi
        .fn()
        .mockResolvedValueOnce([{ sc: 6, oc: 6, p: 15 }])
        .mockResolvedValue([]);
      wrapper = await mountCharts(eq);
      expect(wrapper.findAll(".stub-metric-card").length).toBe(4);
      expect(wrapper.find(".stub-sankey-chart").exists()).toBe(true);
    });
  });

  describe("provided-by sources", () => {
    it("renders provided-by tags when second query returns results", async () => {
      const eq = vi
        .fn()
        .mockResolvedValueOnce([{ sc: 3, oc: 3, p: 5 }])
        .mockResolvedValueOnce([
          { provided_by: "hpoa_edges", count: 500 },
          { provided_by: "gene_to_phenotype", count: 200 },
        ]);
      wrapper = await mountCharts(eq);
      const tags = wrapper.findAll(".provided-by-tag");
      expect(tags.length).toBe(2);
      expect(tags[0].text()).toContain("hpoa_edges");
      expect(tags[0].text()).toContain("500");
    });

    it("does not crash when provided-by query fails", async () => {
      const eq = vi
        .fn()
        .mockResolvedValueOnce([{ sc: 3, oc: 3, p: 5 }])
        .mockRejectedValueOnce(new Error("provided_by column missing"));
      wrapper = await mountCharts(eq);
      // Should still render charts, just no tags
      expect(wrapper.findAll(".stub-metric-card").length).toBe(4);
      expect(wrapper.findAll(".provided-by-tag").length).toBe(0);
    });
  });

  describe("safeInforesId sanitization", () => {
    it("sanitizes special characters from inforesId", async () => {
      const eq = vi
        .fn()
        .mockResolvedValueOnce([{ sc: 2, oc: 1, p: 2 }])
        .mockResolvedValue([]);
      wrapper = await mountCharts(eq, {
        inforesId: "infores:hpo-annotations'; DROP TABLE--",
      });
      // The first call's SQL should contain the sanitized ID (special chars stripped)
      const callSql = eq.mock.calls[0][0] as string;
      // The semicolon and quote from the injection attempt should be removed
      expect(callSql).not.toContain(";");
      // The sanitized value should only contain alphanumeric, colons, hyphens, underscores
      expect(callSql).toContain("infores:hpo-annotationsDROPTABLE--");
      // Spaces and quotes from the injection are stripped
      expect(callSql).not.toContain("DROP TABLE");
    });
  });

  describe("SQL computed properties", () => {
    it("generates correct SQL containing the inforesId", async () => {
      const eq = vi
        .fn()
        .mockResolvedValueOnce([{ sc: 6, oc: 6, p: 15 }])
        .mockResolvedValue([]);
      wrapper = await mountCharts(eq);

      // Check that metric cards receive SQL with the inforesId
      const metricCards = wrapper.findAllComponents(StubKGMetricCard);
      expect(metricCards.length).toBe(4);
      for (const card of metricCards) {
        expect(card.props("sql")).toContain("infores:hpo-annotations");
      }

      // Check chord chart SQL
      const chord = wrapper.findComponent(StubChordChart);
      expect(chord.props("sql")).toContain("infores:hpo-annotations");
      expect(chord.props("sql")).toContain("subject_category");

      // Check predicate table SQL
      const predTable = wrapper.findComponent(StubPredicateTable);
      expect(predTable.props("sql")).toContain("infores:hpo-annotations");

      // Check sankey chart SQL (complex tier)
      const sankey = wrapper.findComponent(StubSankeyChart);
      expect(sankey.props("sql")).toContain("infores:hpo-annotations");
      expect(sankey.props("sql")).toContain("LIMIT 50");
    });
  });

  describe("event handlers", () => {
    it("emits filter-predicate with biolink: prefix on predicate selection", async () => {
      const eq = vi
        .fn()
        .mockResolvedValueOnce([{ sc: 2, oc: 1, p: 2 }])
        .mockResolvedValue([]);
      wrapper = await mountCharts(eq);

      // Trigger the predicate-selected event on the stub
      const predTable = wrapper.findComponent(StubPredicateTable);
      predTable.vm.$emit("predicate-selected", "has_phenotype");
      await wrapper.vm.$nextTick();

      expect(wrapper.emitted("filter-predicate")).toBeTruthy();
      expect(wrapper.emitted("filter-predicate")![0]).toEqual([
        "biolink:has_phenotype",
      ]);
    });
  });
});
