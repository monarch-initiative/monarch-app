import { expect, test } from "vitest";
import AppTextbox from "@/components/AppTextbox.vue";
import { emitted, mount } from "./setup";

test("Button clears text", async () => {
  const props = { modelValue: "dummy text" };
  const wrapper = mount(AppTextbox, { props });
  await wrapper.find("button").trigger("click");
  expect(emitted(wrapper)[0]).toBe("");
});
