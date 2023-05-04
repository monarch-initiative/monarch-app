import { expect, test } from "vitest";
import AppButton from "@/components/AppButton.vue";
import { mount } from "./setup";

test("Renders as link", () => {
  const props = { text: "Test link", to: "https://google.com/" };
  const wrapper = mount(AppButton, { props });
  expect(wrapper.find("a").exists()).toBeTruthy();
});

test("Renders as button", () => {
  const props = { text: "Test link", onClick: () => null };
  const wrapper = mount(AppButton, { props });
  expect(wrapper.find("button").exists()).toBeTruthy();
});
