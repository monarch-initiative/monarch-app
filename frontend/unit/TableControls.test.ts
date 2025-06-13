import type { Component } from "vue";
import { expect, test } from "vitest";
import TableControls from "@/components/TheTableContols.vue";
import { emitted, mount } from "./setup";

const data = [
  { name: "abc", score: 9, details: [1, 2] },
  { name: "def", score: -1, details: [2, 1, 3] },
  { name: "def", score: 2, details: [1] },
  { name: "abc", score: 4, details: [2, 1] },
  { name: "ghi", score: NaN, details: [1] },
] as const;

const props = {
  rows: data,
  perPage: 10,
  start: 1,
  total: 123,
};

test("Changes per page", async () => {
  const wrapper = mount(TableControls as unknown as Component, { props });
  await wrapper.find(".controls div:nth-child(1) button").trigger("click");
  await wrapper.find("[role='option']").trigger("click");
  expect(emitted(wrapper, "update:perPage")).toEqual([5]);
});

test("Changes pages", async () => {
  const wrapper = mount(TableControls as unknown as Component, { props });
  const nav = wrapper.findAll(".controls div:nth-child(2) button");
  await nav.at(1)?.trigger("click");
  expect(emitted(wrapper, "update:start"));
  await nav.at(2)?.trigger("click");
  expect(emitted(wrapper, "update:start"));
  await nav.at(3)?.trigger("click");
  expect(emitted(wrapper, "update:start"));
  await nav.at(4)?.trigger("click");
  expect(emitted(wrapper, "update:start"));
});

test("Downloads", async () => {
  const wrapper = mount(TableControls as unknown as Component, { props });
  await wrapper.find(".controls div:nth-child(3) button").trigger("click");
  expect(emitted(wrapper, "download")).toEqual([]);
});

test("Terminal page switching buttons", async () => {
  const fiveItemsProps = {
    ...props,
    perPage: 5,
    start: 0,
    total: 5,
  };

  const wrapper = mount(TableControls as unknown as Component, {
    props: fiveItemsProps,
  });
  const navButtons = wrapper
    .findAll(".controls div:nth-child(2) button")
    .slice(1);

  // first, prev, next, last
  expect(navButtons.length).toEqual(4);
  for (const button of navButtons) {
    expect(button.attributes("disabled")).not.toBeUndefined();
  }
});
