import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { mount, type VueWrapper } from "@vue/test-utils";
import { ref, computed } from "vue";
import KGMetricCard from "@/components/dashboard/KGMetricCard.vue";

// Mock the composables and components
const mockExecuteQuery = vi.fn();
const mockRetry = vi.fn();
const mockCleanup = vi.fn();

vi.mock("@/composables/use-sql-query", () => ({
  useSqlQuery: vi.fn(() => ({
    isLoading: ref(false),
    error: ref(null),
    result: ref({
      data: [{ count: 1234 }],
      columns: ["count"],
      rowCount: 1,
      executionTime: 45.2,
      isFromCache: false,
    }),
    lastExecuted: ref(new Date()),
    getSingleValue: computed(() => 1234),
    shouldAutoExecute: computed(() => true),
    executeQuery: mockExecuteQuery,
    retry: mockRetry,
    clearCache: vi.fn(),
    cleanup: mockCleanup,
    validateSQL: vi.fn().mockReturnValue({ isValid: true, errors: [] }),
  })),
}));

vi.mock("@/components/dashboard/BaseChart.vue", () => ({
  default: {
    name: "BaseChart",
    template: `
      <div class="base-chart">
        <div v-if="title" class="chart-title">{{ title }}</div>
        <slot />
      </div>
    `,
    props: [
      "title",
      "isLoading",
      "error",
      "data",
      "sql",
      "showControls",
      "allowExport",
      "showDataPreview",
      "height",
    ],
    emits: ["retry", "export"],
  },
}));

vi.mock("@/components/AppIcon.vue", () => ({
  default: {
    name: "AppIcon",
    template: '<span class="icon">{{ icon }}</span>',
    props: ["icon"],
  },
}));

describe("KGMetricCard", () => {
  let wrapper: VueWrapper<any>;

  beforeEach(async () => {
    vi.clearAllMocks();
    // Reset the mock to ensure clean state
    const { useSqlQuery } = await import("@/composables/use-sql-query");
    vi.mocked(useSqlQuery).mockReturnValue({
      isLoading: ref(false),
      error: ref(null),
      result: ref({
        data: [{ count: 1234 }],
        columns: ["count"],
        rowCount: 1,
        executionTime: 45.2,
        isFromCache: false,
      }),
      lastExecuted: ref(new Date()),
      getSingleValue: computed(() => 1234),
      shouldAutoExecute: computed(() => true),
      executeQuery: mockExecuteQuery,
      retry: mockRetry,
      clearCache: vi.fn(),
      cleanup: mockCleanup,
      validateSQL: vi.fn().mockReturnValue({ isValid: true, errors: [] }),
    } as any);
    mockExecuteQuery.mockReset();
    mockRetry.mockReset();
    mockCleanup.mockReset();
  });

  afterEach(() => {
    if (wrapper) {
      try {
        wrapper.unmount();
      } catch {
        // Ignore unmount errors
      }
    }
    wrapper = null as any;
    vi.resetAllMocks();
  });

  describe("basic rendering", () => {
    it("should render with basic props", () => {
      wrapper = mount(KGMetricCard, {
        props: {
          title: "Total Nodes",
          dataSource: "nodes",
          sql: "SELECT COUNT(*) as count FROM nodes",
        },
      });

      expect(wrapper.find(".chart-title").text()).toBe("Total Nodes");
      expect(wrapper.find(".value").text()).toBe("1,234");
    });

    it("should render with subtitle and description", () => {
      wrapper = mount(KGMetricCard, {
        props: {
          title: "Total Nodes",
          dataSource: "nodes",
          sql: "SELECT COUNT(*) as count FROM nodes",
          subtitle: "in knowledge graph",
          description: "Total number of entities in the graph",
        },
      });

      expect(wrapper.find(".metric-subtitle").text()).toBe(
        "in knowledge graph",
      );
      expect(wrapper.find(".metric-description").text()).toBe(
        "Total number of entities in the graph",
      );
    });
  });

  describe("value formatting", () => {
    it("should format numbers correctly", () => {
      wrapper = mount(KGMetricCard, {
        props: {
          title: "Total Count",
          dataSource: "test",
          sql: "SELECT 1234567 as count",
          format: "number",
        },
      });

      expect(wrapper.find(".value").text()).toBe("1,234");
    });

    it("should format percentages correctly", async () => {
      const { useSqlQuery } = await import("@/composables/use-sql-query");
      vi.mocked(useSqlQuery).mockReturnValueOnce({
        isLoading: ref(false),
        error: ref(null),
        result: ref({
          data: [{ rate: 0.856 }],
          columns: ["rate"],
          rowCount: 1,
          executionTime: 45.2,
          isFromCache: false,
        }),
        lastExecuted: ref(new Date()),
        getSingleValue: computed(() => 0.856),
        shouldAutoExecute: computed(() => true),
        executeQuery: mockExecuteQuery,
        retry: mockRetry,
        clearCache: vi.fn(),
        cleanup: mockCleanup,
        validateSQL: vi.fn().mockReturnValue({ isValid: true, errors: [] }),
      } as any);

      wrapper = mount(KGMetricCard, {
        props: {
          title: "Success Rate",
          dataSource: "test",
          sql: "SELECT 0.856 as rate",
          format: "percentage",
        },
      });

      expect(wrapper.find(".value").text()).toBe("85.6%");
    });

    it("should format currency correctly", async () => {
      const { useSqlQuery } = await import("@/composables/use-sql-query");
      vi.mocked(useSqlQuery).mockReturnValueOnce({
        isLoading: ref(false),
        error: ref(null),
        result: ref({
          data: [{ amount: 12345.67 }],
          columns: ["amount"],
          rowCount: 1,
          executionTime: 45.2,
          isFromCache: false,
        }),
        lastExecuted: ref(new Date()),
        getSingleValue: computed(() => 12345.67),
        shouldAutoExecute: computed(() => true),
        executeQuery: mockExecuteQuery,
        retry: mockRetry,
        clearCache: vi.fn(),
        cleanup: mockCleanup,
        validateSQL: vi.fn().mockReturnValue({ isValid: true, errors: [] }),
      } as any);

      wrapper = mount(KGMetricCard, {
        props: {
          title: "Cost",
          dataSource: "test",
          sql: "SELECT 12345.67 as amount",
          format: "currency",
        },
      });

      expect(wrapper.find(".value").text()).toBe("$12,345.67");
    });

    it("should show dash for null values", async () => {
      const { useSqlQuery } = await import("@/composables/use-sql-query");
      vi.mocked(useSqlQuery).mockReturnValueOnce({
        isLoading: ref(false),
        error: ref(null),
        result: ref({
          data: [],
          columns: [],
          rowCount: 0,
          executionTime: 45.2,
          isFromCache: false,
        }),
        lastExecuted: ref(new Date()),
        getSingleValue: computed(() => null),
        shouldAutoExecute: computed(() => true),
        executeQuery: mockExecuteQuery,
        retry: mockRetry,
        clearCache: vi.fn(),
        cleanup: mockCleanup,
        validateSQL: vi.fn().mockReturnValue({ isValid: true, errors: [] }),
      } as any);

      wrapper = mount(KGMetricCard, {
        props: {
          title: "Empty Result",
          dataSource: "test",
          sql: "SELECT NULL as value",
        },
      });

      expect(wrapper.find(".value").text()).toBe("—");
    });
  });

  describe("trend indicators", () => {
    it("should show positive trend", () => {
      wrapper = mount(KGMetricCard, {
        props: {
          title: "Growth",
          dataSource: "test",
          sql: "SELECT 100 as value",
          showTrend: true,
          trendValue: 15.5,
        },
      });

      const trend = wrapper.find(".metric-trend");
      expect(trend.exists()).toBe(true);
      expect(trend.classes()).toContain("positive");
      expect(trend.find(".icon").text()).toBe("trending-up");
      expect(trend.text()).toContain("15.5%");
    });

    it("should show negative trend", () => {
      wrapper = mount(KGMetricCard, {
        props: {
          title: "Decline",
          dataSource: "test",
          sql: "SELECT 100 as value",
          showTrend: true,
          trendValue: -8.2,
        },
      });

      const trend = wrapper.find(".metric-trend");
      expect(trend.classes()).toContain("negative");
      expect(trend.find(".icon").text()).toBe("trending-down");
      expect(trend.text()).toContain("8.2%");
    });

    it("should show neutral trend", () => {
      wrapper = mount(KGMetricCard, {
        props: {
          title: "Stable",
          dataSource: "test",
          sql: "SELECT 100 as value",
          showTrend: true,
          trendValue: 0,
        },
      });

      const trend = wrapper.find(".metric-trend");
      expect(trend.classes()).toContain("neutral");
      expect(trend.find(".icon").text()).toBe("minus");
      expect(trend.text()).toContain("0%");
    });

    it("should use custom trend suffix", () => {
      wrapper = mount(KGMetricCard, {
        props: {
          title: "Change",
          dataSource: "test",
          sql: "SELECT 100 as value",
          showTrend: true,
          trendValue: 5,
          trendSuffix: " pts",
        },
      });

      const trend = wrapper.find(".metric-trend");
      expect(trend.text()).toContain("5 pts");
    });
  });

  describe("loading and error states", () => {
    it("should show loading state", async () => {
      const { useSqlQuery } = await import("@/composables/use-sql-query");
      vi.mocked(useSqlQuery).mockReturnValueOnce({
        isLoading: ref(true),
        error: ref(null),
        result: ref(null),
        lastExecuted: ref(new Date()),
        getSingleValue: computed(() => null),
        shouldAutoExecute: computed(() => true),
        executeQuery: mockExecuteQuery,
        retry: mockRetry,
        clearCache: vi.fn(),
        cleanup: mockCleanup,
        validateSQL: vi.fn().mockReturnValue({ isValid: true, errors: [] }),
      } as any);

      wrapper = mount(KGMetricCard, {
        props: {
          title: "Loading Test",
          dataSource: "test",
          sql: "SELECT COUNT(*) as count",
        },
      });

      expect(wrapper.find(".metric-value").classes()).toContain("loading");
    });

    it("should show error state", async () => {
      const { useSqlQuery } = await import("@/composables/use-sql-query");
      vi.mocked(useSqlQuery).mockReturnValueOnce({
        isLoading: ref(false),
        error: ref("Database connection failed"),
        result: ref(null),
        lastExecuted: ref(new Date()),
        getSingleValue: computed(() => null),
        shouldAutoExecute: computed(() => true),
        executeQuery: mockExecuteQuery,
        retry: mockRetry,
        clearCache: vi.fn(),
        cleanup: mockCleanup,
        validateSQL: vi.fn().mockReturnValue({ isValid: true, errors: [] }),
      } as any);

      wrapper = mount(KGMetricCard, {
        props: {
          title: "Error Test",
          dataSource: "test",
          sql: "SELECT COUNT(*) as count",
        },
      });

      expect(wrapper.find(".metric-value").classes()).toContain("error");
    });
  });

  describe("interactions", () => {
    it("should call retry when handleRetry is invoked", async () => {
      wrapper = mount(KGMetricCard, {
        props: {
          title: "Retry Test",
          dataSource: "test",
          sql: "SELECT COUNT(*) as count",
        },
      });

      // Call handleRetry directly since there's no retry button
      await wrapper.vm.handleRetry();

      expect(mockRetry).toHaveBeenCalled();
    });

    it("should emit error event on error", async () => {
      wrapper = mount(KGMetricCard, {
        props: {
          title: "Error Test",
          dataSource: "test",
          sql: "SELECT COUNT(*) as count",
        },
      });

      // Trigger error by making retry fail
      mockRetry.mockRejectedValueOnce(new Error("Test error"));
      await wrapper.vm.handleRetry();

      expect(wrapper.emitted("error")).toBeTruthy();
      expect(wrapper.emitted("error")?.[0][0]).toBe("Test error");
    });

    it("should have correct raw value", async () => {
      wrapper = mount(KGMetricCard, {
        props: {
          title: "Value Change Test",
          dataSource: "test",
          sql: "SELECT 100 as value",
        },
      });

      // Check the computed value directly
      expect(wrapper.vm.rawValue).toBe(1234);
    });
  });

  describe("lifecycle", () => {
    it("should execute query on mount when autoExecute is false", async () => {
      // Wait for mount to complete
      await new Promise(resolve => setTimeout(resolve, 0));
      
      wrapper = mount(KGMetricCard, {
        props: {
          title: "Manual Execute",
          dataSource: "test",
          sql: "SELECT COUNT(*) as count",
          autoExecute: false,
        },
      });

      // Wait for mounted hook
      await wrapper.vm.$nextTick();
      
      expect(mockExecuteQuery).toHaveBeenCalled();
    });

    it("should cleanup on unmount", async () => {
      wrapper = mount(KGMetricCard, {
        props: {
          title: "Cleanup Test",
          dataSource: "test",
          sql: "SELECT COUNT(*) as count",
        },
      });

      await wrapper.vm.$nextTick();
      wrapper.unmount();

      expect(mockCleanup).toHaveBeenCalled();
    });
  });

  describe("bytes and duration formatting", () => {
    it("should format bytes correctly", async () => {
      const { useSqlQuery } = await import("@/composables/use-sql-query");
      vi.mocked(useSqlQuery).mockReturnValueOnce({
        isLoading: ref(false),
        error: ref(null),
        result: ref({
          data: [{ size: 1048576 }],
          columns: ["size"],
          rowCount: 1,
          executionTime: 45.2,
          isFromCache: false,
        }),
        lastExecuted: ref(new Date()),
        getSingleValue: computed(() => 1048576),
        shouldAutoExecute: computed(() => true),
        executeQuery: mockExecuteQuery,
        retry: mockRetry,
        clearCache: vi.fn(),
        cleanup: mockCleanup,
        validateSQL: vi.fn().mockReturnValue({ isValid: true, errors: [] }),
      } as any);

      wrapper = mount(KGMetricCard, {
        props: {
          title: "File Size",
          dataSource: "test",
          sql: "SELECT 1048576 as size",
          format: "bytes",
        },
      });

      expect(wrapper.find(".value").text()).toBe("1 MB");
    });

    it("should format duration correctly", async () => {
      const { useSqlQuery } = await import("@/composables/use-sql-query");
      vi.mocked(useSqlQuery).mockReturnValueOnce({
        isLoading: ref(false),
        error: ref(null),
        result: ref({
          data: [{ duration: 2500 }],
          columns: ["duration"],
          rowCount: 1,
          executionTime: 45.2,
          isFromCache: false,
        }),
        lastExecuted: ref(new Date()),
        getSingleValue: computed(() => 2500),
        shouldAutoExecute: computed(() => true),
        executeQuery: mockExecuteQuery,
        retry: mockRetry,
        clearCache: vi.fn(),
        cleanup: mockCleanup,
        validateSQL: vi.fn().mockReturnValue({ isValid: true, errors: [] }),
      } as any);

      wrapper = mount(KGMetricCard, {
        props: {
          title: "Processing Time",
          dataSource: "test",
          sql: "SELECT 2500 as duration",
          format: "duration",
        },
      });

      expect(wrapper.find(".value").text()).toBe("2.5s");
    });
  });
});
