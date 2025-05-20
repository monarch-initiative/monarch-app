import { expect, test } from "vitest";
import AppNodeText from "@/components/AppNodeText.vue";
import { mount } from "./setup";

test("Renders plain text", async () => {
  const props = { text: "Node name" };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node name");
});

test("Renders bolded text", async () => {
  const props = { text: "Node <b>name</b>" };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node name");
  expect(htmlEl.get("span b").text()).toEqual("name");
});

test("Renders italicized text", async () => {
  const props = { text: "Node <i>name</i>" };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node name");
  expect(htmlEl.get("span i").text()).toEqual("name");
});

test("Renders anchor tags with an href", async () => {
  const props = { text: 'Node <a href="https://example.com/">name</a>' };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node name");
  expect(htmlEl.get("span a").text()).toEqual("name");
  expect(htmlEl.get("span a").attributes("href")).toEqual(
    "https://example.com/",
  );
});

test("Renders superscripted text", async () => {
  const props = { text: "Node <sup>name</sup>" };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node name");
  expect(htmlEl.get("span sup").text()).toEqual("name");
});

test("Renders superscripted as a span in SVG", async () => {
  const props = { text: "Node <sup>name</sup>", isSvg: true };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node name");
  expect(htmlEl.get("span span").text()).toEqual("name");
});

test("Escapes non-whitelisted 'tags'", async () => {
  const props = { text: "Node <test>name</test>" };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node <test>name</test>");
});

test("Renders nested tags", async () => {
  const props = { text: "Node <b>n<sup>am</sup>e</b>" };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node name");
});

test("Renders SVG in a foreignObject tag", async () => {
  const props = { text: "Node name", isSvg: true };

  const svgEl = mount(AppNodeText, { props });
  expect(svgEl.get("foreignobject").text()).toEqual("Node name");
});
