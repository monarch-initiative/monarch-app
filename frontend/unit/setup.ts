import { nextTick, type Component, type ComponentPublicInstance } from "vue";
import { cloneDeep } from "lodash";
import { setupServer } from "msw/node";
import { afterAll, afterEach, beforeAll, beforeEach, vi } from "vitest";
import type { MountingOptions, VueWrapper } from "@vue/test-utils";
import { mount as _mount } from "@vue/test-utils";
import components from "@/global/components";
import plugins from "@/global/plugins";
import router from "@/router";
import { sleep } from "@/util/debug";
import "@/global/icons";
import { handlers } from "../fixtures";

/** run before each test */
beforeEach(async () => {
  /** set default route and wait until ready */
  await router.push("/");
  await router.isReady();
});

/** https://github.com/vuejs/router/issues/615 */
afterAll(async () => {
  await sleep();
});

/** setup mock-service-worker */
const server = setupServer(...handlers);
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

/** util function to wait for api calls to mock */
export const apiCall = async (): Promise<void> => {
  /**
   * why two "flushPromises" calls? see:
   * https://github.com/vuejs/test-utils/issues/137
   */
  await sleep();
  await sleep();
};

/** mount wrapper with standard options */
export const mount = (
  component: Component,
  options: MountingOptions<{ [key: string | number]: unknown }> = {},
  vModel: { [key: string | number]: unknown } = {}
) => {
  /** standard globals */
  options.global = { components, plugins, stubs: { teleport: true } };

  /** deep clone props so nested objects get new instance every mount */
  options.props = cloneDeep(options.props) || {};

  /** implement v-model */
  /** https://github.com/vuejs/test-utils/discussions/279 */
  for (const [prop, value] of Object.entries(vModel)) {
    options.props[prop] = value;
    options.props["onUpdate:" + prop] = async (modelValue: unknown) => {
      await nextTick();
      await wrapper.setProps({ modelValue });
    };
  }

  /** mount */
  const wrapper = _mount(component as any, options);

  return wrapper;
};

/**
 * util to get last emitted event from mounted wrapper. returns array of event
 * props, i.e. $emit("someEvent", prop1, prop2, ...). this only checks emitted
 * model value updates, it doesn't two-way bind like v-model. make sure to only
 * use on components that keep local track of model state and don't rely on
 * parent to do that with v-model.
 */
export const emitted = <T = unknown>(
  wrapper: VueWrapper<ComponentPublicInstance>,
  event = "update:modelValue"
): Array<T> => {
  try {
    return wrapper.emitted()[event].pop() as Array<T>;
  } catch (error) {
    throw new Error(`No "${event}" event emitted`);
  }
};

/** mock functions that will throw error vitest environment */
window.scrollTo = vi.fn(() => null);
