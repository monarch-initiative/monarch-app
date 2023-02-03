import { nextTick } from "vue";
import { mount, emitted } from "../setup";
import AppSelectTags from "@/components/AppSelectTags.vue";

/** some example props for each test */
const props = {
  name: "Tags select",
  options: (search: string) => {
    const ids = search.split(",");
    if (ids.length >= 2)
      return { autoAccept: true, options: ids.map((id) => ({ id })) };
    else
      return {
        options: [
          { id: "fruits" },
          { id: "vegetables", count: 7 },
          { id: "colors", count: 42 },
          { id: "animals" },
        ].filter((entry) => entry.id.includes(search)),
      };
  },
};

/** two-way bound state */
const vModel = { modelValue: [{ id: "animals" }] };

/** expected type of emitted update:modelValue events */
type T = Array<unknown>;

/** nextTick used occasionally here due to useQuery */

test("Buttons click to deselect", async () => {
  const wrapper = mount(AppSelectTags, props, vModel);
  await wrapper.find("button").trigger("click");
  expect(emitted<T>(wrapper)[0].length).toEqual(0);
});

test("Clear button clicks to deselect", async () => {
  const wrapper = mount(AppSelectTags, props, vModel);
  await wrapper.findAll("button")[2].trigger("click");
  expect(emitted<T>(wrapper)[0].length).toEqual(0);
});

test("Types to search", async () => {
  const wrapper = mount(AppSelectTags, props, vModel);
  await wrapper.find("input").trigger("focus");
  await nextTick();
  expect(wrapper.findAll("[role='option']").length).toBe(3);
  await wrapper.find("input").setValue("veg");
  await nextTick();
  expect(wrapper.findAll("[role='option']").length).toBe(1);
});

test("Pastes to auto select", async () => {
  const wrapper = mount(AppSelectTags, props, vModel);
  await wrapper.find("input").setValue("HP:0000322,HP:0001166,HP:0001238");
  await nextTick();
  const buttons = wrapper.findAll("button");
  expect(buttons.at(1)?.text()).toEqual("HP:0000322");
  expect(buttons.at(2)?.text()).toEqual("HP:0001166");
  expect(buttons.at(3)?.text()).toEqual("HP:0001238");
});

test("Clicks to select", async () => {
  const wrapper = mount(AppSelectTags, props, vModel);
  await wrapper.find("input").trigger("focus");
  await nextTick();
  await wrapper.findAll("[role='option']").at(0)?.trigger("click");
  expect(emitted<T>(wrapper)[0].length).toEqual(2);
  await wrapper.findAll("[role='option']").at(0)?.trigger("click");
  expect(emitted<T>(wrapper)[0].length).toEqual(3);
  await wrapper.findAll("[role='option']").at(0)?.trigger("click");
  expect(emitted<T>(wrapper)[0].length).toEqual(4);
});

test("Selects by keyboard", async () => {
  const wrapper = mount(AppSelectTags, props, vModel);
  const input = wrapper.find("input");
  await input.trigger("focus");
  await input.trigger("keydown", { key: "ArrowUp" });
  await input.trigger("keydown", { key: "Enter" });
  expect(emitted<T>(wrapper)[0].length).toEqual(2);
  await input.trigger("keydown", { key: "ArrowUp" });
  await input.trigger("keydown", { key: "Enter" });
  expect(emitted<T>(wrapper)[0].length).toEqual(3);
});
