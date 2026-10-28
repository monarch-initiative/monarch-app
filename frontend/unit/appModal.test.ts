import { afterEach, beforeEach, describe, expect, test } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import AppModal from "@/components/AppModal.vue";

/** the component reads and mutates #app, which does not exist in a bare jsdom */
function appRoot(): HTMLElement {
  let app = document.querySelector<HTMLElement>("#app");
  if (!app) {
    app = document.createElement("div");
    app.id = "app";
    document.body.append(app);
  }
  return app;
}

const open = (label: string) =>
  mount(AppModal, {
    props: { modelValue: true, label },
    attachTo: appRoot(),
    global: { stubs: { AppButton: true } },
  });

describe("AppModal", () => {
  beforeEach(() => {
    appRoot();
  });
  afterEach(() => {
    document.body.innerHTML = "";
  });

  test("the dialog is not inside an aria-hidden subtree", () => {
    // aria-hidden applies to a whole subtree. While it sat on the wrapper, the dialog
    // was hidden along with the backdrop, and #app is inert at the same time -- so a
    // screen reader had nothing to read in either direction.
    const wrapper = open("Association Details");
    const dialog = document.querySelector('[role="dialog"]')!;
    expect(dialog).not.toBeNull();

    for (let node = dialog; node; node = node.parentElement as Element) {
      if (node === document.body) break;
      expect(node.getAttribute("aria-hidden")).not.toBe("true");
    }
    expect(
      document.querySelector(".backdrop")?.getAttribute("aria-hidden"),
    ).toBe("true");
    wrapper.unmount();
  });

  test("escape closes only the topmost modal", async () => {
    const outer = open("outer");
    const inner = open("inner");
    await flushPromises();

    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    await flushPromises();

    expect(inner.emitted("update:modelValue")?.at(-1)).toEqual([false]);
    expect(outer.emitted("update:modelValue")).toBeUndefined();

    inner.unmount();
    outer.unmount();
  });

  test("the page stays hidden until the last modal closes", async () => {
    const app = appRoot();
    const outer = open("outer");
    const inner = open("inner");
    await flushPromises();
    expect(app.getAttribute("inert")).toBe("true");

    // closing the inner one used to hand the background back while the outer was up
    await inner.setProps({ modelValue: false });
    await flushPromises();
    expect(app.getAttribute("inert")).toBe("true");
    expect(app.getAttribute("aria-hidden")).toBe("true");

    await outer.setProps({ modelValue: false });
    await flushPromises();
    expect(app.getAttribute("inert")).toBeNull();
    expect(app.getAttribute("aria-hidden")).toBeNull();

    inner.unmount();
    outer.unmount();
  });

  test("unmounting while open does not leave the page inert", async () => {
    const app = appRoot();
    const wrapper = open("orphan");
    await flushPromises();
    expect(app.getAttribute("inert")).toBe("true");

    wrapper.unmount();
    await flushPromises();
    expect(app.getAttribute("inert")).toBeNull();
  });
});
