import { beforeEach, describe, expect, test } from "vitest";
import { mount } from "@vue/test-utils";
import AppPredicateBadge from "@/components/AppPredicateBadge.vue";

/**
 * Two ways the explainer described the wrong relationship.
 *
 * Both are about the identity of the predicate reaching the explainer, which is
 * why they live together: one substituted a stale predicate, the other a
 * marked-up one.
 */

const association = (
  predicate: string,
  highlighting?: Record<string, string[]>,
) =>
  ({
    subject: "MONDO:0007947",
    subject_label: "Marfan syndrome",
    predicate,
    object: "HP:0001166",
    object_label: "Arachnodactyly",
    ...(highlighting ? { highlighting } : {}),
  }) as never;

const stubs = {
  AppModal: { template: "<div><slot /></div>" },
  AppIcon: true,
  AppLink: true,
  AppButton: true,
  AppPredicateInfo: {
    name: "AppPredicateInfo",
    props: ["predicate"],
    template: `<button :aria-label="'Explain ' + predicate">i</button>`,
  },
};

describe("predicate explainer identity", () => {
  beforeEach(() => localStorage.clear());

  test("search highlighting never reaches the explainer", () => {
    // Solr wraps matches in markup, which is right for the rendered label but is not
    // an identifier: it matches nothing in the biolink model and leaks tags into the
    // accessible name and modal title.
    const wrapper = mount(AppPredicateBadge, {
      props: {
        association: association("biolink:applied_to_treat", {
          predicate: ["biolink:applied_to_<em>treat</em>"],
        }),
        highlight: true,
      },
      global: { stubs },
    });
    const label = wrapper.find("button[aria-label]").attributes("aria-label");
    expect(label).toBe("Explain biolink:applied_to_treat");
    expect(label).not.toContain("<em>");
  });

  test("a reused row passes its new predicate, not the one it was mounted with", async () => {
    // AppTable keys rows by index, so paging or sorting reuses this instance with a
    // different association.
    const wrapper = mount(AppPredicateBadge, {
      props: { association: association("biolink:treats") },
      global: { stubs },
    });
    expect(wrapper.find("button[aria-label]").attributes("aria-label")).toBe(
      "Explain biolink:treats",
    );

    await wrapper.setProps({ association: association("biolink:causes") });
    expect(wrapper.find("button[aria-label]").attributes("aria-label")).toBe(
      "Explain biolink:causes",
    );
  });
});
