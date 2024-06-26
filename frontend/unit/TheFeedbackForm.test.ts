import { expect, test } from "vitest";
import TheFeedbackForm from "@/components/TheFeedbackForm.vue";
import { apiCall, mount } from "./setup";

test("Submits correctly when filled out", async () => {
  /** mount */
  const wrapper = mount(TheFeedbackForm, { attachTo: document.body });

  /** fill out feedback textarea */
  const textarea = wrapper.find("textarea");
  const testMessage = "Test message";
  await textarea.setValue(testMessage);

  /** https://github.com/vuejs/vue-test-utils/issues/1932 */
  (
    await wrapper.find<HTMLButtonElement>("button[type='submit']")
  ).element.focus();
  /** submit form */
  await wrapper.find("form").trigger("submit");

  /** wait for api calls to mock */
  await apiCall();

  /** test status message and expect to be success */
  const link = wrapper.find(".status a");
  expect(link.exists()).toBeTruthy();
});
