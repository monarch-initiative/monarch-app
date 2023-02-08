/** jest setup and util funcs */

import { ComponentPublicInstance, nextTick } from "vue";
import {
  MountingOptions,
  VueWrapper,
  mount as vueMount,
} from "@vue/test-utils";
import { toHaveNoViolations } from "jest-axe";
import { setupServer } from "msw/node";
import fetch from "node-fetch";
import { cloneDeep } from "lodash";
import router from "@/router";
import components from "@/global/components";
import plugins from "@/global/plugins";
import { sleep } from "@/util/debug";
import { handlers } from "./fixtures";
import "@/global/icons";

/** mock global/window/browser functions */
window.scrollTo = jest.fn();
HTMLCanvasElement.prototype.getContext = jest.fn();
window.ResizeObserver = jest
  .fn()
  .mockImplementation(() => ({ observe: jest.fn(), disconnect: jest.fn() }));
window.fetch = jest.fn().mockImplementation(fetch);
window.Request = jest.fn().mockImplementation();
window.caches = {
  delete: jest.fn(),
  open: jest.fn().mockImplementation(() => ({
    match: jest.fn(),
    put: jest.fn(),
  })),
} as unknown as CacheStorage;

/**
 * "fast-forward" lodash debounce calls
 * https://gist.github.com/apieceofbart/d28690d52c46848c39d904ce8968bb27
 * https://github.com/facebook/jest/issues/3465
 * https://gist.github.com/j-v/6222ff5e91c18f506aff86853626c5c0
 */
jest.mock("lodash", () => {
  const module = jest.requireActual("lodash");
  module.debounce = jest.fn((fn) => {
    fn.cancel = jest.fn();
    return fn;
  });
  return module;
});

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

/** add axe to jest */
expect.extend(toHaveNoViolations);

/** setup mock-service-worker for node.js (jest) */
const server = setupServer(...handlers);
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

/** util function to wait for api calls to mock */
export const apiCall = async (): Promise<void> => {
  /**
   * why two "flushPromises" calls? see:
   * https://github.com/mswjs/msw/issues/1163
   * https://github.com/vuejs/test-utils/issues/137
   */
  await sleep();
  await sleep();
};

/** generic props type */
type Props = Record<string | number, unknown>;

/** generic vModel type */
type VModel = Record<string | number, unknown>;

/** mount wrapper with standard options */
export const mount = <Component>(
  component: Component,
  props: Props = {},
  vModel: VModel = {},
  options: MountingOptions<Props> = {}
) => {
  type Wrapper = VueWrapper<ComponentPublicInstance<Component>>;

  /** implement v-model */
  for (const [prop, value] of Object.entries(vModel)) {
    props[prop] = value;
    /** https://github.com/vuejs/test-utils/discussions/279 */
    props["onUpdate:" + prop] = async (modelValue: unknown) => {
      await nextTick();
      await wrapper.setProps({ modelValue });
    };
  }

  /** deep clone props so nested objects get new instance every mount */
  options.props = cloneDeep(props);

  /** standard globals */
  options.global = { components, plugins, stubs: { teleport: true } };

  // eslint-disable-next-line
  const wrapper: Wrapper = vueMount(component, options as MountingOptions<any>);
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
