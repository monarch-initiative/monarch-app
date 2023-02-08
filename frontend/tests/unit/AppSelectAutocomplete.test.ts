import { mount, emitted } from "../setup";
import AppSelectAutocomplete from "@/components/AppSelectAutocomplete.vue";

/** some example props for each test */
const props = {
  name: "Autocomplete select",
  options: (search: string) =>
    [
      { name: "fruits" },
      { name: "vegetables", count: 7 },
      { name: "colors", count: 42 },
      { name: "animals" },
    ].filter((entry) => entry.name.includes(search)),
};

/** expected type of emitted update:modelValue events */
type T = Array<unknown>;

test("Types to search", async () => {
  const wrapper = mount(AppSelectAutocomplete, props);
  await wrapper.find("input").trigger("focus");
  expect(wrapper.findAll("[role='option']").length).toBe(4);
  await wrapper.find("input").setValue("veg");
  await wrapper.find("input").trigger("focus");
  expect(wrapper.findAll("[role='option']").length).toBe(1);
});

test("Selects by keyboard", async () => {
  const wrapper = mount(AppSelectAutocomplete, props);
  const input = wrapper.find("input");
  await input.trigger("focus");
  await input.trigger("keydown", { key: "ArrowUp" });
  await input.trigger("keydown", { key: "Enter" });
  expect(emitted<T>(wrapper)[0]).toEqual("animals");
});

test("Selects by mouse", async () => {
  const wrapper = mount(AppSelectAutocomplete, props);
  await wrapper.find("input").trigger("focus");
  await wrapper.find("[role='option']").trigger("click");
  expect(emitted<T>(wrapper)[0]).toEqual("fruits");
});
