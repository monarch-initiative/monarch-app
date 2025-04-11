import { expect, test } from "vitest";
import AppNodeText from "@/components/AppNodeText.vue";
import { mount } from "./setup";

test("Renders plain text", async () => {
  const props = { text: "Node name" };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node name");

  const svgEl = mount(AppNodeText, { props: { ...props, isSvg: true } });
  expect(svgEl.get("tspan").text()).toEqual("Node name");
});

test("Renders bolded text", async () => {
  const props = { text: "Node <b>name</b>" };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node name");
  expect(htmlEl.get("span b").text()).toEqual("name");

  const svgEl = mount(AppNodeText, { props: { ...props, isSvg: true } });
  const tspans = svgEl.findAll("tspan");
  expect(tspans.length).toEqual(2);
  expect(tspans[0].text()).toEqual("Node name");
  expect(tspans[1].attributes("class")).toEqual("svg-bold");
  expect(tspans[1].text()).toEqual("name");
});

test("Renders italicized text", async () => {
  const props = { text: "Node <i>name</i>" };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node name");
  expect(htmlEl.get("span i").text()).toEqual("name");

  const svgEl = mount(AppNodeText, { props: { ...props, isSvg: true } });
  const tspans = svgEl.findAll("tspan");
  expect(tspans.length).toEqual(2);
  expect(tspans[0].text()).toEqual("Node name");
  expect(tspans[1].attributes("class")).toEqual("svg-italic");
  expect(tspans[1].text()).toEqual("name");
});

test("Renders anchor tags with an href", async () => {
  const props = { text: 'Node <a href="https://example.com/">name</a>' };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node name");
  expect(htmlEl.get("span a").text()).toEqual("name");
  expect(htmlEl.get("span a").attributes("href")).toEqual(
    "https://example.com/",
  );

  const svgEl = mount(AppNodeText, { props: { ...props, isSvg: true } });
  expect(svgEl.get("tspan").text()).toEqual("Node name");
  expect(svgEl.get("tspan a").text()).toEqual("name");
  expect(svgEl.get("tspan a").attributes("href")).toEqual(
    "https://example.com/",
  );
});

test("Renders superscripted text", async () => {
  const props = { text: "Node <sup>name</sup>" };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node name");
  expect(htmlEl.get("span sup").text()).toEqual("name");

  const svgEl = mount(AppNodeText, { props: { ...props, isSvg: true } });
  const tspans = svgEl.findAll("tspan");
  expect(tspans.length).toEqual(3);
  expect(tspans[0].text()).toEqual("Node name");
  expect(tspans[1].attributes("class")).toEqual("svg-superscript");
  expect(tspans[1].attributes("dy")).toEqual("-1ex");
  expect(tspans[1].text()).toEqual("name");
  expect(tspans[2].attributes("dy")).toEqual("+1ex");
  expect(tspans[2].text()).toEqual("");
});

test("Escapes non-whitelisted 'tags'", async () => {
  const props = { text: "Node <test>name</test>" };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node <test>name</test>");

  const svgEl = mount(AppNodeText, { props: { ...props, isSvg: true } });
  expect(svgEl.get("tspan").text()).toEqual("Node <test>name</test>");
});

test("Renders nested tags", async () => {
  const props = { text: "Node <b>n<sup>am</sup>e</b>" };

  const htmlEl = mount(AppNodeText, { props });
  expect(htmlEl.get("span").text()).toEqual("Node name");

  const svgEl = mount(AppNodeText, { props: { ...props, isSvg: true } });
  expect(svgEl.get("tspan").text()).toEqual("Node name");
});
