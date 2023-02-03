import { mount } from "../setup";
import AppLink from "@/components/AppLink.vue";

test("Renders as link", () => {
  const props = { to: "https://google.com/" };
  const wrapper = mount(AppLink, props);
  expect(wrapper.find("a").exists()).toBeTruthy();
});

test("Renders as router-link", () => {
  const props = { to: "/about" };
  const wrapper = mount(AppLink, props);
  expect(wrapper.findComponent({ name: "router-link" }).exists()).toBeTruthy();
});
