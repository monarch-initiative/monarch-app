import { expect, test } from "vitest";
import TheTableOfContents from "@/components/TheTableOfContents.vue";
import { mount } from "./setup";

/**
 * The hierarchy widget is gated on a term actually having parents or children,
 * not just on its category.
 */
const node = (
  category: string,
  hierarchy: { super_classes?: unknown[]; sub_classes?: unknown[] } | null,
) =>
  ({
    id: "LOINC:35094-2",
    name: "Blood pressure panel",
    category,
    node_hierarchy: hierarchy,
    association_counts: [],
  }) as never;

const parent = {
  id: "LOINC:CC-LP18033-8",
  name: "Amino acids Component Class",
};

test("Shows the hierarchy when a clinical measurement has a parent", () => {
  const wrapper = mount(TheTableOfContents, {
    props: {
      node: node("biolink:ClinicalMeasurement", { super_classes: [parent] }),
    },
  });
  expect(wrapper.find(".toc-hier").exists()).toBe(true);
});

test("Shows the hierarchy when a term only has children", () => {
  const wrapper = mount(TheTableOfContents, {
    props: {
      node: node("biolink:ClinicalMeasurement", { sub_classes: [parent] }),
    },
  });
  expect(wrapper.find(".toc-hier").exists()).toBe(true);
});

test("Hides the hierarchy when a term has neither parents nor children", () => {
  const wrapper = mount(TheTableOfContents, {
    props: {
      node: node("biolink:ClinicalMeasurement", {
        super_classes: [],
        sub_classes: [],
      }),
    },
  });
  expect(wrapper.find(".toc-hier").exists()).toBe(false);
});

test("Hides the hierarchy when the node reports none at all", () => {
  const wrapper = mount(TheTableOfContents, {
    props: { node: node("biolink:ClinicalMeasurement", null) },
  });
  expect(wrapper.find(".toc-hier").exists()).toBe(false);
});

test("Still hides the hierarchy for categories that never show it", () => {
  const wrapper = mount(TheTableOfContents, {
    props: { node: node("biolink:Gene", { super_classes: [parent] }) },
  });
  expect(wrapper.find(".toc-hier").exists()).toBe(false);
});

test("Renders without a node", () => {
  const wrapper = mount(TheTableOfContents, { props: { node: null } });
  expect(wrapper.find(".toc-hier").exists()).toBe(false);
});
