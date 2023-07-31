import { expect, test } from "vitest";
import AppSelectAutocomplete from "@/components/AppSelectAutocomplete.vue";
import { emitted, mount } from "./setup";

/** some example props for each test */
const props = {
  name: "Autocomplete select",
  options: (search: string) =>
    [
      { label: "fruits" },
      { label: "vegetables", count: 7 },
      { label: "colors", count: 42 },
      { label: "animals" },
    ].filter((entry) => entry.label.includes(search)),
};

/** expected type of emitted update:modelValue events */
type Emitted = Array<unknown>;

test("Types to search", async () => {
  const wrapper = mount(AppSelectAutocomplete, { props });
  await wrapper.find("input").trigger("focus");
  expect(wrapper.findAll("[role='option']").length).toBe(4);
  await wrapper.find("input").setValue("veg");
  await wrapper.find("input").trigger("focus");
  expect(wrapper.findAll("[role='option']").length).toBe(1);
});

test("Selects by keyboard", async () => {
  const wrapper = mount(AppSelectAutocomplete, { props });
  const input = wrapper.find("input");
  await input.trigger("focus");
  await input.trigger("keydown", { key: "ArrowUp" });
  await input.trigger("keydown", { key: "Enter" });
  expect(emitted<Emitted>(wrapper)[0]).toEqual("animals");
});

test("Selects by mouse", async () => {
  const wrapper = mount(AppSelectAutocomplete, { props });
  await wrapper.find("input").trigger("focus");
  await wrapper.find("[role='option']").trigger("click");
  expect(emitted<Emitted>(wrapper)[0]).toEqual("fruits");
});
