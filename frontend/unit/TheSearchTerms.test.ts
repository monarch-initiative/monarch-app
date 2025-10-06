import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { mount, VueWrapper } from "@vue/test-utils";
import Suggestions from "@/components/TheSearchTerms.vue";

vi.mock("vue-router", () => {
  const push = vi.fn(() => Promise.resolve());
  return { useRouter: () => ({ push }) };
});
vi.mock("@/api/categories", () => ({
  getCategoryIcon: vi.fn(() => "icon-stub"),
}));
vi.mock("@/components/AppNodeText.vue", () => ({
  default: {
    name: "AppNodeText",
    template: "<span data-test='app-node-text'><slot /></span>",
  },
}));
vi.mock("@/data/toolEntityConfig", () => ({
  ENTITY_MAP: {
    "Ehlers-Danlos syndrome": { id: "MONDO:0020066", to: "section-phenotypes" },
    FBN1: { id: "HGNC:3603", to: "section-phenotypes" },
    "Down syndrome": { id: "MONDO:0008608", to: "section-models" },
    "cystic fibrosis": { id: "MONDO:0009061", to: "section-variants" },
  },
}));

const flushTimers = async () => {
  vi.runAllTimers();
  await Promise.resolve();
};

describe("Suggestions.vue", () => {
  let wrapper: VueWrapper<any>;

  beforeEach(() => {
    vi.useFakeTimers();
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
          AppIcon: { template: '<span data-test="app-icon"></span>' },
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

  //  renders suggestions list and label
  it("renders a list of suggestion pairs", () => {
    const rows = wrapper.findAll(".suggestion-pair");
    expect(rows.length).toBe(4); // expects 4 items in your sample
    expect(wrapper.find(".label").text()).toMatch(/Examples of relationships/i);
  });

  //  clicking a suggestion triggers router.push with /:id#hash
  it("navigates with router.push to the right path+hash on click", async () => {
    const { useRouter } = await import("vue-router");
    const router = useRouter() as any;

    const first = wrapper.findAll(".suggestion-pair")[0];
    await first.trigger("click");

    expect(router.push).toHaveBeenCalledWith({
      path: "/MONDO:0020066",
      hash: "#section-phenotypes",
    });
  });
});
