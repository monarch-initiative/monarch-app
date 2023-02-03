import { emitted } from "./../setup";
import { mount } from "../setup";
import AppTextbox from "@/components/AppTextbox.vue";

test("Button clears text", async () => {
  const props = { modelValue: "dummy text" };
  const wrapper = mount(AppTextbox, props);
  await wrapper.find("button").trigger("click");
  expect(emitted(wrapper)[0]).toBe("");
});
