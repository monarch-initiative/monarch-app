import PageHelp from "../src/pages/help/PageHelp.vue";
import { expect, test } from "vitest";
import { apiCall, mount } from "./setup";

test("Help page renders uptimerobot statuses", async () => {
  /** mount and wait until async rendering is done */
  const wrapper = mount(PageHelp);

  /** wait for api calls to mock */
  await apiCall();

  /**
   * check that various statuses exist. fixture data contains all possible
   * status types from uptimerobot. check that all of them get converted to and
   * displayed as appropriate status components.
   */
  expect(wrapper.find("[data-code='success']").exists()).toBeTruthy();
  expect(wrapper.find("[data-code='error']").exists()).toBeTruthy();
  expect(wrapper.find("[data-code='paused']").exists()).toBeTruthy();
  expect(wrapper.find("[data-code='unknown']").exists()).toBeTruthy();
});
