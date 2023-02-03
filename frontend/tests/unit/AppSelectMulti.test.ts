import { mount, emitted } from "../setup";
import AppSelectMulti from "@/components/AppSelectMulti.vue";

/** some example props for each test */
const props = {
  name: "Multi select",
  options: [
    { id: "fruits", count: 0 },
    { id: "vegetables", count: 7 },
    { id: "colors", count: 42 },
    { id: "animals", count: 999 },
  ],
};

/** two-way bound state */
const vModel = { modelValue: [{ id: "vegetables" }] };

test("Opens/closes on click", async () => {
  const wrapper = mount(AppSelectMulti, props, vModel);
  const button = wrapper.find("button");
  await button.trigger("click");
  expect(wrapper.find("[role='listbox']").exists()).toBe(true);
  await button.trigger("click");
  expect(wrapper.find("[role='listbox']").exists()).toBe(false);
  await button.trigger("click");
  expect(wrapper.find("[role='listbox']").exists()).toBe(true);
  await button.trigger("blur");
  expect(wrapper.find("[role='listbox']").exists()).toBe(false);
});

test("Opens/closes on keyboard", async () => {
  const wrapper = mount(AppSelectMulti, props, vModel);
  const button = wrapper.find("button");
  await button.trigger("click");
  expect(wrapper.find("[role='listbox']").exists()).toBe(true);
  await button.trigger("keydown", { key: "Escape" });
});

/** expected type of emitted update:modelValue events */
type T = Array<unknown>;

test("Selects by click", async () => {
  const wrapper = mount(AppSelectMulti, props, vModel);
  const button = wrapper.find("button");
  await button.trigger("click");
  await wrapper.findAll("[role='option']").at(1)?.trigger("click");
  expect(emitted<T>(wrapper)[0].length).toEqual(2);
  await wrapper.findAll("[role='option']").at(3)?.trigger("click");
  expect(emitted<T>(wrapper)[0].length).toEqual(3);
  await wrapper.findAll("[role='option']").at(4)?.trigger("click");
  expect(emitted<T>(wrapper)[0].length).toEqual(4);
});

test("Selects by keyboard", async () => {
  const wrapper = mount(AppSelectMulti, props, vModel);
  const button = wrapper.find("button");
  await button.trigger("click");
  await button.trigger("keydown", { key: "ArrowUp" });
  await button.trigger("keydown", { key: "Enter" });
  expect(emitted<T>(wrapper)[0].length).toEqual(2);
  await button.trigger("keydown", { key: "ArrowUp" });
  await button.trigger("keydown", { key: "ArrowUp" });
  await button.trigger("keydown", { key: "Enter" });
  expect(emitted<T>(wrapper)[0].length).toEqual(3);
  await button.trigger("keydown", { key: "ArrowUp" });
  await button.trigger("keydown", { key: "Enter" });
  expect(emitted<T>(wrapper)[0].length).toEqual(4);
});

test("Selects all by click", async () => {
  const wrapper = mount(AppSelectMulti, props, vModel);
  const button = wrapper.find("button");
  await button.trigger("click");
  const option = wrapper.find("[role='option']");
  await option.trigger("click");
  expect(emitted<T>(wrapper)[0].length).toEqual(4);
  await option.trigger("click");
  expect(emitted<T>(wrapper)[0].length).toEqual(0);
});
