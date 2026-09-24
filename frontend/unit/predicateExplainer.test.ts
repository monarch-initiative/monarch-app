import { beforeEach, describe, expect, test, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import AppPredicateBadge from "@/components/AppPredicateBadge.vue";
import AppPredicateInfo from "@/components/AppPredicateInfo.vue";

/** AppButton renders a real button so `$el` is the element the popover anchors to */
const buttonStub = {
  name: "AppButton",
  props: ["ariaLabel"],
  template: `<button v-bind="$attrs"><slot /></button>`,
};

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

describe("predicate explainer is a popover, not a nested modal", () => {
  beforeEach(() => localStorage.clear());

  test("Escape closes the explainer without reaching an enclosing modal", async () => {
    // AppModal listens for Escape on window and is always attached, so an explainer
    // opened inside the association-details modal must stop the event or both close.
    const onWindowEscape = vi.fn();
    window.addEventListener("keydown", onWindowEscape);

    const wrapper = mount(AppPredicateInfo, {
      props: { predicate: "biolink:treats" },
      attachTo: document.body,
      global: { stubs: { AppButton: buttonStub, AppStatus: true, AppLink: true } },
    });

    await wrapper.find("button").trigger("click");
    await flushPromises();
    const popover = document.querySelector<HTMLElement>('[role="dialog"]');
    expect(popover).not.toBeNull();

    popover!.dispatchEvent(
      new KeyboardEvent("keydown", { key: "Escape", bubbles: true }),
    );
    await flushPromises();

    expect(document.querySelector('[role="dialog"]')).toBeNull();
    expect(onWindowEscape).not.toHaveBeenCalled();

    window.removeEventListener("keydown", onWindowEscape);
    wrapper.unmount();
  });

  test("opening marks the trigger expanded and closing restores focus to it", async () => {
    const wrapper = mount(AppPredicateInfo, {
      props: { predicate: "biolink:treats" },
      attachTo: document.body,
      global: { stubs: { AppButton: buttonStub, AppStatus: true, AppLink: true } },
    });

    const trigger = wrapper.find("button");
    expect(trigger.attributes("aria-expanded")).toBe("false");

    await trigger.trigger("click");
    await flushPromises();
    expect(trigger.attributes("aria-expanded")).toBe("true");

    const popover = document.querySelector<HTMLElement>('[role="dialog"]');
    popover!.dispatchEvent(
      new KeyboardEvent("keydown", { key: "Escape", bubbles: true }),
    );
    await flushPromises();

    expect(trigger.attributes("aria-expanded")).toBe("false");
    expect(document.activeElement).toBe(trigger.element);
    wrapper.unmount();
  });
});

describe("views that spell out the definition do not also offer the popover", () => {
  test("the icon is suppressed when explain is false", () => {
    // The node-page and dashboard detail modals render the definition inline. A second
    // route to the same text is noise, and inside a modal the popover has to out-stack
    // the overlay to be clickable at all.
    const wrapper = mount(AppPredicateBadge, {
      props: { association: association("biolink:treats"), explain: false },
      global: { stubs },
    });
    expect(wrapper.find("button[aria-label]").exists()).toBe(false);
  });

  test("the icon is offered by default", () => {
    const wrapper = mount(AppPredicateBadge, {
      props: { association: association("biolink:treats") },
      global: { stubs },
    });
    expect(wrapper.find("button[aria-label]").exists()).toBe(true);
  });
});
