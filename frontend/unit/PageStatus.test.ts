import { expect, test, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import * as uptimeApi from "@/api/uptime";
import PageStatus from "@/pages/knowledgeGraph/PageStatus.vue";

test("renders all uptimerobot statuses", async () => {
  vi.spyOn(uptimeApi, "getUptimes").mockResolvedValue([
    { code: "success", text: "API", link: "https://status/api" },
    { code: "error", text: "API (dev)", link: "https://status/api-dev" },
    { code: "paused", text: "Scheduler", link: "https://status/scheduler" },
    { code: "unknown", text: "Legacy", link: "https://status/legacy" },
  ]);

  const wrapper = mount(PageStatus, {
    global: {
      stubs: {
        AppBreadcrumb: true,
        ThePageTitle: true,
        AppSection: true,
        AppGallery: true,
        AppLink: true,
        AppStatus: true,
      },
    },
  });
  await flushPromises();

  expect(wrapper.find('[data-test="status-success"]').exists()).toBe(true);
  expect(wrapper.find('[data-test="status-error"]').exists()).toBe(true);
  expect(wrapper.find('[data-test="status-paused"]').exists()).toBe(true);
  expect(wrapper.find('[data-test="status-unknown"]').exists()).toBe(true);
});
