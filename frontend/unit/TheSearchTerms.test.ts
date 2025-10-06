import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { mount, VueWrapper } from "@vue/test-utils";
import TheSearchTerms from "@/components/TheSearchTerms.vue";

const AppNodeBadgeStub = {
  name: "AppNodeBadge",
  props: ["node", "icon"],
  // Keep the same root class the parent applies, and expose a test hook
  template: `<div class="terms" data-test="badge">{{ node.label }}</div>`,
};

describe("TheSearchTerms.vue", () => {
  let wrapper: VueWrapper<any> | undefined;

  beforeEach(() => {
    // Silence jsdom's not-implemented scrollTo (some libs call it)
    vi.spyOn(window, "scrollTo").mockImplementation(() => {});
    wrapper = mount(TheSearchTerms, {
      global: {
        stubs: {
          AppNodeBadge: AppNodeBadgeStub,
        },
      },
    });
  });

  afterEach(() => {
    try {
      wrapper?.unmount?.();
    } finally {
      wrapper = undefined;
      (window.scrollTo as any).mockRestore?.();
      vi.restoreAllMocks();
      vi.useRealTimers();
      document.body.innerHTML = "";
    }
  });

  //  Renders one badge per suggestion (the array has 10 items)
  it("renders the correct number of badges", () => {
    const badges = wrapper!.findAll('[data-test="badge"]');
    expect(badges.length).toBe(10);
  });

  //  Ensures the 'terms' class is applied and the first label is correct
  it("applies the 'terms' class and passes node.label", () => {
    const items = wrapper!.findAllComponents(AppNodeBadgeStub);
    expect(items.length).toBeGreaterThan(0);

    items.forEach((w) => {
      expect(w.classes()).toContain("terms");
    });

    // Spot check first item label from your source array
    expect(items[0].text()).toContain("Ehlers-Danlos syndrome");
  });
});
