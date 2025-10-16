import { expect, test } from "vitest";
import PageHelp from "@/pages/knowledgeGraph/PageHelp.vue";
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
  expect(wrapper.find(".success").exists()).toBeTruthy();
  expect(wrapper.find(".error").exists()).toBeTruthy();
  expect(wrapper.find(".paused").exists()).toBeTruthy();
  expect(wrapper.find(".unknown").exists()).toBeTruthy();
});
