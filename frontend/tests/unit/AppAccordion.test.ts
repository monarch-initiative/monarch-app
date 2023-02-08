import { mount } from "../setup";
import AppAccordion from "@/components/AppAccordion.vue";

test("Expands and collapses", async () => {
  const props = { text: "Test accordion" };
  const slots = { default: "Hello world" };
  const wrapper = mount(AppAccordion, props, {}, { slots });
  const button = wrapper.find("button");
  expect(wrapper.text()).not.toContain("Hello world");
  await button.trigger("click");
  expect(wrapper.text()).toContain("Hello world");
});
