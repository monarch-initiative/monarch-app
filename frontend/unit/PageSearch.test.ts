import { beforeEach, describe, expect, test, vi } from "vitest";
import { mount } from "@vue/test-utils";
import SearchSuggestions from "@/components/TheSearchSuggestions.vue";
import PageSearch from "@/pages/knowledgeGraph/PageSearch.vue";
import router from "@/router";
import * as domUtils from "@/util/dom";

vi.mock("@/data/knowledgeGraphConfig", () => ({
  ENTITY_MAP: {
    "Multicystic kidney dysplasia": {
      id: "MONDO:0015988",
      to: "overview",
    },
  },
  TOOL_LINKS: [{ label: "Test Tool", to: "/kg/test", external: false }],
}));

describe("PageSearch.vue", () => {
  beforeEach(async () => {
    router.push("/kg");
    await router.isReady();
  });

  test("renders search input and tool links", () => {
    const wrapper = mount(PageSearch, {
      global: { plugins: [router] },
    });

    expect(wrapper.find("input").exists()).toBe(true);
    expect(wrapper.findAll(".tool").length).toBeGreaterThan(0);
  });

  test("calls waitFor when input is focused", async () => {
    const mockInput = document.createElement("input");
    const waitForSpy = vi
      .spyOn(domUtils, "waitFor")
      .mockResolvedValue(mockInput);

    const wrapper = mount(PageSearch, {
      global: { plugins: [router] },
    });

    const input = wrapper.find("input");
    await input.trigger("focus");

    expect(waitForSpy).toHaveBeenCalledWith("input");

    waitForSpy.mockRestore();
  });

  test("navigates to results when search submitted", async () => {
    const wrapper = mount(PageSearch, {
      global: { plugins: [router] },
    });

    const comp = wrapper.getComponent({ name: "AppSelectAutocomplete" });
    await comp.vm.$emit("change", "kidney", "kidney");

    await wrapper.vm.$nextTick();
    await new Promise((r) => setTimeout(r, 0)); // Allow router to update

    expect(router.currentRoute.value.fullPath).toContain("search=kidney");
    expect(router.currentRoute.value.name).toBe("KnowledgeGraphResults");
  });

  test("handles suggestion click and scroll", async () => {
    const pushSpy = vi.spyOn(router, "push").mockResolvedValue();

    const wrapper = mount(PageSearch, {
      global: { plugins: [router] },
    });

    const suggestion = wrapper.findComponent(SearchSuggestions);
    expect(suggestion.exists()).toBe(true);

    await suggestion.vm.$emit("select", "Multicystic kidney dysplasia");

    // Wait for DOM update
    await wrapper.vm.$nextTick();

    expect(pushSpy).toHaveBeenCalled();
    expect(pushSpy.mock.calls[0][0]).toMatchObject({
      path: "/MONDO:0015988",
      hash: "#overview",
    });

    pushSpy.mockRestore();
  });
});
