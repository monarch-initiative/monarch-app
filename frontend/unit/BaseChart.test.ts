import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { mount, type VueWrapper } from "@vue/test-utils";
import BaseChart from "@/components/dashboard/BaseChart.vue";

// Mock ECharts
const mockChart = {
  setOption: vi.fn(),
  resize: vi.fn(),
  dispose: vi.fn(),
};

vi.mock("echarts", () => ({
  init: vi.fn(() => mockChart),
}));

// Mock components
vi.mock("@/components/AppButton.vue", () => ({
  default: {
    name: "AppButton",
    template: "<button @click=\"$emit('click')\"><slot /></button>",
    props: ["size", "variant"],
    emits: ["click"],
  },
}));

vi.mock("@/components/AppIcon.vue", () => ({
  default: {
    name: "AppIcon",
    template: "<span>{{ name }}</span>",
    props: ["name"],
  },
}));

describe("BaseChart", () => {
  let wrapper: VueWrapper<any>;

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock window resize
    global.addEventListener = vi.fn();
    global.removeEventListener = vi.fn();
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  describe("rendering", () => {
    it("should render without title", () => {
      wrapper = mount(BaseChart);

      expect(wrapper.find(".chart-title").exists()).toBe(false);
      expect(wrapper.find(".chart-content").exists()).toBe(true);
    });

    it("should render with title", () => {
      wrapper = mount(BaseChart, {
        props: {
          title: "Test Chart",
        },
      });

      expect(wrapper.find(".chart-title").exists()).toBe(true);
      expect(wrapper.find(".chart-title").text()).toBe("Test Chart");
    });

    it("should render with custom height", () => {
      wrapper = mount(BaseChart, {
        props: {
          height: "500px",
        },
      });

      const chartContent = wrapper.find(".chart-content");
      expect(chartContent.attributes("style")).toContain("height: 500px");
    });

    it("should show controls when enabled", () => {
      wrapper = mount(BaseChart, {
        props: {
          title: "Test Chart",
          sql: "SELECT * FROM test",
          showControls: true,
        },
      });

      expect(wrapper.find(".chart-controls").exists()).toBe(true);
      expect(wrapper.findAll("button")).toHaveLength(2); // SQL and Export buttons
    });

    it("should hide controls when disabled", () => {
      wrapper = mount(BaseChart, {
        props: {
          title: "Test Chart",
          sql: "SELECT * FROM test",
          showControls: false,
        },
      });

      expect(wrapper.find(".chart-controls").exists()).toBe(false);
    });
  });

  describe("loading state", () => {
    it("should show loading state", () => {
      wrapper = mount(BaseChart, {
        props: {
          isLoading: true,
          loadingText: "Loading data...",
        },
      });

      expect(wrapper.find(".chart-loading").exists()).toBe(true);
      expect(wrapper.find(".chart-loading").text()).toContain(
        "Loading data...",
      );
      expect(wrapper.classes()).toContain("loading");
    });

    it("should hide loading state when not loading", () => {
      wrapper = mount(BaseChart, {
        props: {
          isLoading: false,
        },
      });

      expect(wrapper.find(".chart-loading").exists()).toBe(false);
      expect(wrapper.classes()).not.toContain("loading");
    });

    it("should use default loading text", () => {
      wrapper = mount(BaseChart, {
        props: {
          isLoading: true,
        },
      });

      expect(wrapper.find(".chart-loading").text()).toContain(
        "Loading chart data...",
      );
    });
  });

  describe("error state", () => {
    it("should show error state", () => {
      wrapper = mount(BaseChart, {
        props: {
          error: "Failed to load data",
        },
      });

      expect(wrapper.find(".chart-error").exists()).toBe(true);
      expect(wrapper.find(".chart-error").text()).toContain(
        "Failed to load data",
      );
      expect(wrapper.classes()).toContain("error");
    });

    it("should hide error state when no error", () => {
      wrapper = mount(BaseChart, {
        props: {
          error: null,
        },
      });

      expect(wrapper.find(".chart-error").exists()).toBe(false);
      expect(wrapper.classes()).not.toContain("error");
    });

    it("should show retry button when allowed", () => {
      wrapper = mount(BaseChart, {
        props: {
          error: "Failed to load data",
          allowRetry: true,
        },
      });

      const retryButton = wrapper.find(".chart-error button");
      expect(retryButton.exists()).toBe(true);
      expect(retryButton.text()).toBe("Retry");
    });

    it("should emit retry event when retry button is clicked", async () => {
      wrapper = mount(BaseChart, {
        props: {
          error: "Failed to load data",
          allowRetry: true,
        },
      });

      const retryButton = wrapper.find(".chart-error button");
      await retryButton.trigger("click");

      expect(wrapper.emitted("retry")).toBeTruthy();
    });
  });

  describe("SQL display", () => {
    it("should show SQL button when SQL is provided", () => {
      wrapper = mount(BaseChart, {
        props: {
          title: "Test Chart",
          sql: "SELECT * FROM test",
        },
      });

      const buttons = wrapper.findAll("button");
      const sqlButton = buttons.find((button) =>
        button.text().includes("Show SQL"),
      );
      expect(sqlButton).toBeDefined();
    });

    it("should toggle SQL display", async () => {
      wrapper = mount(BaseChart, {
        props: {
          title: "Test Chart",
          sql: "SELECT * FROM test",
        },
      });

      // Initially hidden
      expect(wrapper.find(".chart-sql").exists()).toBe(false);

      // Click to show
      const buttons = wrapper.findAll("button");
      const sqlButton = buttons.find((button) =>
        button.text().includes("Show SQL"),
      );
      expect(sqlButton).toBeDefined();

      if (sqlButton) {
        await sqlButton.trigger("click");

        expect(wrapper.find(".chart-sql").exists()).toBe(true);
        expect(wrapper.find(".chart-sql pre").text()).toBe(
          "SELECT * FROM test",
        );

        // Click to hide
        await sqlButton.trigger("click");
        expect(wrapper.find(".chart-sql").exists()).toBe(false);
      }
    });
  });

  describe("data preview", () => {
    const sampleData = [
      { id: 1, name: "Alice", age: 25 },
      { id: 2, name: "Bob", age: 30 },
      { id: 3, name: "Charlie", age: 35 },
    ];

    it("should show data preview when enabled", () => {
      wrapper = mount(BaseChart, {
        props: {
          data: sampleData,
          showDataPreview: true,
        },
      });

      expect(wrapper.find(".chart-data-preview").exists()).toBe(true);
      expect(wrapper.find(".data-table").exists()).toBe(true);
    });

    it("should hide data preview when disabled", () => {
      wrapper = mount(BaseChart, {
        props: {
          data: sampleData,
          showDataPreview: false,
        },
      });

      expect(wrapper.find(".chart-data-preview").exists()).toBe(false);
    });

    it("should display correct data in preview table", () => {
      wrapper = mount(BaseChart, {
        props: {
          data: sampleData,
          showDataPreview: true,
        },
      });

      const table = wrapper.find(".data-table");
      const headers = table.findAll("th");
      const rows = table.findAll("tbody tr");

      // Check headers
      expect(headers).toHaveLength(3);
      expect(headers[0].text()).toBe("id");
      expect(headers[1].text()).toBe("name");
      expect(headers[2].text()).toBe("age");

      // Check data rows
      expect(rows).toHaveLength(3);
      expect(rows[0].findAll("td")[1].text()).toBe("Alice");
    });

    it("should limit preview to 5 rows", () => {
      const largeData = Array.from({ length: 10 }, (_, i) => ({
        id: i + 1,
        name: `User ${i + 1}`,
      }));

      wrapper = mount(BaseChart, {
        props: {
          data: largeData,
          showDataPreview: true,
        },
      });

      const rows = wrapper.findAll("tbody tr");
      expect(rows).toHaveLength(5);
    });
  });

  describe("chart initialization", () => {
    it("should initialize ECharts on mount", async () => {
      const { init } = await import("echarts");
      wrapper = mount(BaseChart);

      // Wait for next tick to ensure onMounted is called
      await wrapper.vm.$nextTick();

      expect(init).toHaveBeenCalled();
    });

    it("should cleanup chart on unmount", async () => {
      wrapper = mount(BaseChart);
      await wrapper.vm.$nextTick();

      wrapper.unmount();

      expect(mockChart.dispose).toHaveBeenCalled();
    });

    it("should handle window resize", async () => {
      wrapper = mount(BaseChart);
      await wrapper.vm.$nextTick();

      // Simulate window resize
      const resizeHandler = (global.addEventListener as any).mock.calls.find(
        (call: any) => call[0] === "resize",
      )?.[1];

      if (resizeHandler) {
        resizeHandler();
        expect(mockChart.resize).toHaveBeenCalled();
      }
    });
  });

  describe("export functionality", () => {
    it("should emit export event when export button is clicked", async () => {
      wrapper = mount(BaseChart, {
        props: {
          title: "Test Chart",
          allowExport: true,
        },
      });

      const buttons = wrapper.findAll("button");
      const exportButton = buttons.find((button) =>
        button.text().includes("Export"),
      );
      expect(exportButton).toBeDefined();

      if (exportButton) {
        await exportButton.trigger("click");
        expect(wrapper.emitted("export")).toBeTruthy();
        expect(wrapper.emitted("export")?.[0][0]).toEqual(mockChart);
      }
    });

    it("should not show export button when disabled", () => {
      wrapper = mount(BaseChart, {
        props: {
          title: "Test Chart",
          allowExport: false,
        },
      });

      const buttons = wrapper.findAll("button");
      expect(buttons).toHaveLength(0); // No SQL provided, no export allowed
    });
  });

  describe("exposed methods", () => {
    it("should expose chart methods", async () => {
      wrapper = mount(BaseChart);
      await wrapper.vm.$nextTick();

      const vm = wrapper.vm as any;
      expect(vm.chart).toBeDefined();
      expect(vm.updateChart).toBeDefined();
      expect(vm.handleResize).toBeDefined();
      expect(vm.cleanup).toBeDefined();
    });

    it("should update chart with options", async () => {
      wrapper = mount(BaseChart);
      await wrapper.vm.$nextTick();

      const options = { title: { text: "Test" } };
      const vm = wrapper.vm as any;
      vm.updateChart(options);

      expect(mockChart.setOption).toHaveBeenCalledWith(options, true);
    });
  });
});
