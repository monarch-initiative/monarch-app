import type { Component } from "vue";
import { expect, test } from "vitest";
import AppTable, { type Cols } from "@/components/AppTable.vue";
import { emitted, mount } from "./setup";

/** some example props */
const data = [
  { name: "abc", score: 9, details: [1, 2] },
  { name: "def", score: -1, details: [2, 1, 3] },
  { name: "def", score: 2, details: [1] },
  { name: "abc", score: 4, details: [2, 1] },
  { name: "ghi", score: NaN, details: [1] },
] as const;
type Datum = (typeof data)[number];
type Keys = keyof Datum;
const cols: Cols<Keys> = [
  {
    slot: "name",
    key: "name",
    heading: "Name",
    align: "left",
    sortable: true,
  },
  {
    slot: "score",
    key: "score",
    heading: "Score",
    sortable: true,
  },
  {
    slot: "details",
    key: "details",
    heading: "Details",
    align: "left",
    sortable: true,
  },
  {
    slot: "arbitrary",
    heading: "Arbitrary",
    align: "right",
  },
];
const props = {
  cols,
  rows: data,
  sort: { key: "score", direction: "up" },
  perPage: 10,
  start: 1,
  total: 123,
  search: "",
  filterOptions: { score: [{ id: "numbers" }, { id: "nulls" }] },
  selectedFilters: { score: [{ id: "numbers" }] },
};

test("Changes sort", async () => {
  const wrapper = mount(AppTable as unknown as Component, { props });
  await wrapper.findAll("thead button").at(0)?.trigger("click");
  expect(emitted(wrapper, "update:sort")[0]).toEqual({
    key: "name",
    direction: "down",
  });
});

test("Changes filter", async () => {
  const wrapper = mount(AppTable as unknown as Component, { props });
  const button = wrapper.findAll("thead button").at(2);
  await button?.trigger("click");
  await wrapper.findAll("[role='option']").at(1)?.trigger("click");
  await button?.trigger("keydown", { key: "Escape" });
  expect(emitted(wrapper, "update:selectedFilters")).toEqual([{ score: [] }]);
  await button?.trigger("click");
  await wrapper.findAll("[role='option']").at(2)?.trigger("click");
  await button?.trigger("keydown", { key: "Escape" });
  expect(emitted(wrapper, "update:selectedFilters")).toEqual([
    {
      score: [{ id: "nulls" }],
    },
  ]);
});

test("Changes per page", async () => {
  const wrapper = mount(AppTable as unknown as Component, { props });
  await wrapper.find(".controls div:nth-child(1) button").trigger("click");
  await wrapper.find("[role='option']").trigger("click");
  expect(emitted(wrapper, "update:perPage")).toEqual([5]);
});

test("Changes pages", async () => {
  const wrapper = mount(AppTable as unknown as Component, { props });
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

test("Changes search", async () => {
  const wrapper = mount(AppTable as unknown as Component, { props });
  await wrapper.find("input").setValue("test search");
  expect(emitted(wrapper, "update:search")).toEqual(["test search"]);
});

test("Downloads", async () => {
  const wrapper = mount(AppTable as unknown as Component, { props });
  await wrapper.find(".controls div:nth-child(3) button").trigger("click");
  expect(emitted(wrapper, "download")).toEqual([]);
});
