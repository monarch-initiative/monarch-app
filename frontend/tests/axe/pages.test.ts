import { nextTick } from "vue";
import router, { routes } from "@/router";
import { axe } from "jest-axe";
import { mount, apiCall } from "../setup";
import App from "@/App.vue";

/** get list of page paths to check */
const pages = routes
  /** exclude fuzzy-matched paths and other specific pages */
  .filter(
    (route) => !["Node", "NodeRaw", "NotFound"].includes(String(route.name))
  )
  /** paths to navigate to */
  .map((route) => route.path)
  /** specific paths to check */
  .concat(["/disease/MONDO:012345"]);

test(
  "Page accessibility checks",
  async () => {
    /** mount app */
    const wrapper = mount(App);

    /** go through each page/route */
    for (const page of pages) {
      /** log progress */
      console.info(`\n========== Testing page ${page} ==========\n`);

      /** navigate to new page */
      router.push(page);
      await router.isReady();

      /** wait until async rendering is done */
      await nextTick();
      /** wait for api calls to mock */
      await apiCall();

      /** analyze rendered html with axe */
      expect(await axe(wrapper.element)).toHaveNoViolations();

      /** special checks on testbed page */
      if (page === "Testbed") {
        await wrapper.find(".select-single button").trigger("click");
        expect(await axe(wrapper.element)).toHaveNoViolations();

        await wrapper.find(".select-multi button").trigger("click");
        expect(await axe(wrapper.element)).toHaveNoViolations();

        await wrapper.find(".select-tags input").trigger("focus");
        expect(await axe(wrapper.element)).toHaveNoViolations();

        await wrapper.find(".select-autocomplete input").trigger("focus");
        expect(await axe(wrapper.element)).toHaveNoViolations();
      }
    }
  },
  /** allow plenty of seconds per page */
  pages.length * 20 * 1000
);
