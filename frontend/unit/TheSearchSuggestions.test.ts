import { nextTick } from "vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { mount, VueWrapper } from "@vue/test-utils";
import Suggestions from "@/components/TheSearchSuggestions.vue";

// --- test doubles / stubs ---
vi.mock("vue-router", () => {
  const push = vi.fn(() => Promise.resolve());
  return {
    useRouter: () => ({ push }),
  };
});

vi.mock("@/api/categories", () => ({
  getCategoryIcon: vi.fn(() => "icon-stub"),
}));

vi.mock("@/components/AppNodeText.vue", () => ({
  default: {
    name: "AppNodeText",
    template: "<span data-test=app-node-text><slot /></span>",
  },
}));

// Provide an ENTITY_MAP that matches cases used in tests
vi.mock("@/data/toolEntityConfig", () => ({
  ENTITY_MAP: {
    "Ehlers-Danlos syndrome": { id: "MONDO:0020066", to: "section-phenotypes" },
    FBN1: { id: "HGNC:3603", to: "section-phenotypes" },
    "Down syndrome": { id: "MONDO:0008608", to: "section-models" },
    "cystic fibrosis": { id: "MONDO:0009061", to: "section-variants" },
  },
}));

// Utility to flush setTimeout
const flushTimers = async () => {
  // run the 1s timeout inside handleSuggestionClick
  vi.runAllTimers();
  await Promise.resolve();
};

describe("Suggestions.vue", () => {
  let wrapper: VueWrapper<any>;

  beforeEach(() => {
    vi.useFakeTimers();
    // Spy on scrollTo since component calls window.scrollTo
    vi.spyOn(window, "scrollTo").mockImplementation(() => {});

    document.body.innerHTML = `
      <div id="app">
        <div id="section-phenotypes" style="height:20px"></div>
        <div id="section-models" style="height:20px"></div>
        <div id="section-variants" style="height:20px"></div>
      </div>`;

    wrapper = mount(Suggestions, {
      global: {
        stubs: {
          AppIcon: {
            template: '<span data-test="app-icon"></span>',
          },
        },
      },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
    wrapper.unmount();
    document.body.innerHTML = "";
  });
  // renders suggestions list and label
  it("renders a list of suggestion pairs", () => {
    const rows = wrapper.findAll(".suggestion-pair");
    expect(rows.length).toBeGreaterThan(0);
    // From the sample there are 4 items
    expect(rows.length).toBe(4);
    expect(wrapper.find(".label").text()).toMatch(/Examples of relationships/i);
  });
  // clicking a suggestion triggers router.push with /:id#hash
  it("navigates with router.push to the right path+hash on click", async () => {
    const { useRouter } = await import("vue-router");
    const router = useRouter() as any;

    // Click the first suggestion (Ehlers-Danlos syndrome → Phenotypes)
    const first = wrapper.findAll(".suggestion-pair")[0];
    await first.trigger("click");

    expect(router.push).toHaveBeenCalledWith({
      path: "/MONDO:0020066",
      hash: "#section-phenotypes",
    });
  });
  // after navigation, delayed smooth-scroll is invoked
  it("scrolls smoothly to the target element after route render and delay", async () => {
    // Click triggers push → nextTick → setTimeout(1000) → scrollToHashWithOffset
    const first = wrapper.findAll(".suggestion-pair")[0];
    await first.trigger("click");

    // Simulate component render completion
    await nextTick();

    // Execute the delayed timer
    await flushTimers();

    // The component uses window.scrollTo with { top, behavior: 'smooth' }
    expect(window.scrollTo).toHaveBeenCalled();
    const call = (window.scrollTo as any).mock.calls.at(-1)?.[0];
    expect(call).toMatchObject({ behavior: "smooth" });
  });

  //  guard clause: no navigation when mapping is missing id
  it("is resilient when ENTITY_MAP has no matching id (no navigation)", async () => {
    // Temporarily remount with a broken ENTITY_MAP for the first item name
    const { ENTITY_MAP } = await import("@/data/toolEntityConfig");
    // @ts-ignore override for test
    ENTITY_MAP["Ehlers-Danlos syndrome"].id = undefined;

    const fresh = mount(Suggestions, {
      global: { stubs: { AppIcon: true, AppNodeText: true } },
    });

    const { useRouter } = await import("vue-router");
    const router = useRouter() as any;

    const first = fresh.findAll(".suggestion-pair")[0];
    await first.trigger("click");

    expect(router.push).not.toHaveBeenCalled();

    fresh.unmount();
  });
  // stubs for AppIcon/AppNodeText render as expected
  it("passes category icons and node text stubs correctly", () => {
    //  ensure our AppIcon/AppNodeText stubs render per suggestion
    const icons = wrapper.findAll('[data-test="app-icon"]');
    expect(icons.length).toBeGreaterThan(0);

    const texts = wrapper.findAll('[data-test="app-node-text"]');
    expect(texts.length).toBeGreaterThan(0);
  });
});
