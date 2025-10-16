/**
 * - Validate title text derived from the node's category mapping.
 * - Ensure parents/current/children render with truncation class.
 * - Verify the inline child list respects `childLimit` and that the modal shows
 *   the remaining children when "+ more…" is clicked.
 * - Exercise the `labelOf` fallback (id → label) when name/label are missing.
 */

import { defineComponent } from "vue";
import { describe, expect, it } from "vitest";
import { mount, RouterLinkStub } from "@vue/test-utils";
import SectionHeirarchy from "@/pages/node/SectionHierarchy.vue"; //

/**
 * Minimal AppModal stub:
 *
 * - Accepts v-model (modelValue) and label props.
 * - Emits update:modelValue like a proper v-model component.
 * - Renders slot content only when open (modelValue === true).
 */
const AppModalStub = defineComponent({
  name: "AppModal",
  props: {
    modelValue: { type: Boolean, default: false },
    label: { type: String, default: "" },
  },
  emits: ["update:modelValue"],
  template: `<div v-if="modelValue" data-stub="modal"><slot /></div>`,
});
/**
 * Helper to construct a Node-like object with predictable hierarchy shape. Lets
 * each test override category/name/parents/children as needed.
 */
function makeNode({
  category = "biolink:Disease",
  name = "Ehlers-Danlos syndrome, hypermobility",
  parents = ["Parent A", "Parent B"],
  children = [
    "Child 1",
    "Child 2",
    "Child 3",
    "Child 4",
    "Child 5",
    "Child 6",
    "Child 7",
    "Child 8",
  ],
}: {
  category?: string;
  name?: string;
  parents?: string[];
  children?: string[];
}) {
  return {
    id: "MONDO:0000000",
    name,
    category,
    node_hierarchy: {
      super_classes: parents.map((p, i) => ({ id: `P${i + 1}`, name: p })),
      // First child intentionally has only an id to exercise labelOf fallback.
      sub_classes: children.map((c, i) =>
        i === 0 ? { id: `C${i + 1}` } : { id: `C${i + 1}`, name: c },
      ),
    },
  } as any;
}

describe("TocHier.vue", () => {
  it("renders title using category mapping", () => {
    const wrapper = mount(SectionHeirarchy, {
      props: { node: makeNode({}) },
      global: { stubs: { RouterLink: RouterLinkStub, AppModal: AppModalStub } },
    });

    // Title should read "<MappedCategory> hierarchy" (e.g., "Disease hierarchy").
    expect(wrapper.find(".toc-hier-title").text().toLowerCase()).toContain(
      "disease hierarchy",
    );
  });

  it("renders parent rows with truncating links", () => {
    const node = makeNode({
      parents: [
        "A very very very long parent name that should truncate",
        "Parent B",
      ],
    });
    const wrapper = mount(SectionHeirarchy, {
      props: { node },
      global: { stubs: { RouterLink: RouterLinkStub, AppModal: AppModalStub } },
    });

    // Parent rows exist and use the truncation class (.row-text).
    const parents = wrapper.findAll(".parents .parent-row .row-text");
    expect(parents.length).toBe(2);
    expect(parents[0].classes()).toContain("row-text");
    // We can’t assert actual CSS truncation, but text presence confirms binding.
    expect(parents[0].text()).toContain("A very very very long parent name");
  });

  it("renders current row with truncation", () => {
    const wrapper = mount(SectionHeirarchy, {
      props: {
        node: makeNode({
          name: "A very very very long current node name that should truncate",
        }),
      },
      global: { stubs: { RouterLink: RouterLinkStub, AppModal: AppModalStub } },
    });

    const current = wrapper.find(".current-row .row-text");
    expect(current.exists()).toBe(true);
    expect(current.classes()).toContain("row-text");
    expect(current.text()).toContain("A very very very long current node name");
  });

  it('shows only first N children inline and a "+ more…" button for the rest (default limit = 6)', () => {
    const node = makeNode({
      children: ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"], // 8 total
    });
    const wrapper = mount(SectionHeirarchy, {
      props: { node },
      global: { stubs: { RouterLink: RouterLinkStub, AppModal: AppModalStub } },
    });

    // By default, childLimit is 6 (via computed).
    const inlineChildren = wrapper.findAll(".children .child-row");
    expect(inlineChildren.length).toBe(6);

    // The “+ more…” button should indicate remaining children (8 - 6 = 2).
    const moreBtn = wrapper.get("button.more");
    expect(moreBtn.text()).toMatch(/\+\s*2 more/i);
  });

  it("respects childLimit prop", async () => {
    const node = makeNode({ children: ["C1", "C2", "C3", "C4", "C5"] }); // 5 total
    const wrapper = mount(SectionHeirarchy, {
      props: { node, childLimit: 3 },
      global: { stubs: { RouterLink: RouterLinkStub, AppModal: AppModalStub } },
    });

    // With limit 3, only 3 children are inline and 2 are hidden behind modal.
    expect(wrapper.findAll(".children .child-row").length).toBe(3);

    const moreBtn = wrapper.get("button.more");
    expect(moreBtn.text()).toMatch(/\+\s*2 more/i);
  });

  it('opens modal and lists remaining children when clicking "+ more…"', async () => {
    const node = makeNode({
      children: ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"], // 8 total, 6 inline, 2 in modal
    });
    const wrapper = mount(SectionHeirarchy, {
      props: { node },
      global: { stubs: { RouterLink: RouterLinkStub, AppModal: AppModalStub } },
      attachTo: document.body, // ensure event bubbling works in JSDOM
    });

    // Clicking "+ more…" toggles v-model to true, so the stub renders slot content.
    await wrapper.get("button.more").trigger("click");

    // Remaining children (after the first 6) should be rendered in the modal list.
    const items = wrapper.findAll(".hier-modal-list li");
    expect(items.length).toBe(2);

    // Modal title should reflect pluralization and include the node name.
    expect(wrapper.find(".modal-title").text().toLowerCase()).toContain(
      "subclasses of",
    );
  });

  it("labelOf fallback uses id when name/label missing (child row)", () => {
    // makeNode creates first child with id only (“C1”), exercising the fallback.
    const node = makeNode({
      children: ["OnlyIdChild", "C2", "C3", "C4", "C5", "C6"],
    });

    const wrapper = mount(SectionHeirarchy, {
      props: { node },
      global: { stubs: { RouterLink: RouterLinkStub, AppModal: AppModalStub } },
    });

    const firstChildText = wrapper
      .find(".children .child-row .row-text")
      .text();
    expect(firstChildText).toMatch(/^C1$/); // falls back to id
  });
});
