import { expect, test } from "vitest";
import AppMarkdown from "@/components/AppMarkdown.vue";
import { mount } from "./setup";

test("Renders some simple markdown", () => {
  const props = { source: "**Hello** _World_ [test link](google.com)" };
  const wrapper = mount(AppMarkdown, { props });
  expect(wrapper.find("strong").exists()).toBeTruthy(); /** look for bold */
  expect(wrapper.find("em").exists()).toBeTruthy(); /** look for italics */
  expect(wrapper.find("a").exists()).toBeTruthy(); /** look for link */
});
