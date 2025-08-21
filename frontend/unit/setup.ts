import { nextTick } from "vue";
import type { Component } from "vue";
import { cloneDeep } from "lodash";
import { setupServer } from "msw/node";
import { afterAll, afterEach, beforeAll, vi } from "vitest";
import type { ComponentMountingOptions, VueWrapper } from "@vue/test-utils";
import { mount as _mount } from "@vue/test-utils";
import components from "@/global/components";
import plugins from "@/global/plugins";
import { sleep } from "@/util/debug";
import { handlers } from "../fixtures";
import "@/global/icons";

/** setup mock-service-worker */
const server = setupServer(...handlers);
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

/** util function to wait for api calls to mock */
export const apiCall = async (): Promise<void> => {
  /**
   * wait for mocks to finish. multiple sleeps needed because msw wraps
   * callbacks in multiple promises. more arbitrary sleeps may be needed in
   * future, depending on msw implementation details. see:
   * https://github.com/vuejs/test-utils/issues/137
   */
  await sleep(10);
  await sleep(10);
  await sleep(10);
};

/** mount wrapper with standard options */
export const mount = (
  component: Component,
  options: ComponentMountingOptions<unknown> = {},
  vModel: { [key: PropertyKey]: unknown } = {},
) => {
  /** standard globals */
  options.global = { components, plugins, stubs: { teleport: true } };

  /** deep clone props so nested objects get new instance every mount */
  options.props = cloneDeep<typeof options.props>(options.props);

  /** implement v-model */
  /** https://github.com/vuejs/test-utils/discussions/279 */
  if (options.props) {
    for (const [prop, value] of Object.entries(vModel)) {
      options.props[prop] = value;
      options.props["onUpdate:" + prop] = async (modelValue: unknown) => {
        await nextTick();
        await wrapper.setProps({ modelValue });
      };
    }
  }

  /** mount */
  const wrapper = _mount(component, options);

  return wrapper;
};

/**
 * util to get last emitted event from mounted wrapper. returns array of event
 * props, i.e. $emit("someEvent", prop1, prop2, ...). this only checks emitted
 * model value updates, it doesn't two-way bind like v-model. make sure to only
 * use on components that keep local track of model state and don't rely on
 * parent to do that with v-model.
 */
export const emitted = <Event = unknown>(
  wrapper: VueWrapper,
  event = "update:modelValue",
): Array<Event> => {
  try {
    return wrapper.emitted()[event].pop() as Array<Event>;
  } catch (error) {
    throw Error(`No "${event}" event emitted`);
  }
};

/** mock functions that will throw error vitest environment */
Object.defineProperty(window, 'scrollTo', {
  value: vi.fn(() => null),
  writable: true
});

// Mock for JSDOM virtual console to suppress scrollTo errors
const originalConsoleError = console.error;
console.error = (message, ...args) => {
  if (typeof message === 'string' && message.includes('window.scrollTo')) {
    return; // Suppress scrollTo errors
  }
  originalConsoleError(message, ...args);
};

/** ensure components are properly cleaned up between tests */
afterEach(() => {
  // Force cleanup of any remaining Vue instances
  if (global.gc) {
    global.gc();
  }
});

