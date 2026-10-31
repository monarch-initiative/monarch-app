import { afterEach, beforeEach, expect, test, vi } from "vitest";

/** the acknowledgement is module state, so each test imports a fresh copy */
const load = async () => {
  vi.resetModules();
  const { useResearchUseAcknowledgement } =
    await import("@/composables/use-research-use-acknowledgement");
  return useResearchUseAcknowledgement();
};

beforeEach(() => window.sessionStorage.clear());
afterEach(() => {
  vi.restoreAllMocks();
});

test("starts unacknowledged and remembers an acknowledgement for the session", async () => {
  const first = await load();
  expect(first.acknowledged.value).toBe(false);
  first.acknowledge();
  expect(first.acknowledged.value).toBe(true);

  const reloaded = await load();
  expect(reloaded.acknowledged.value).toBe(true);
});

test("is shared by every caller on the page", async () => {
  const { useResearchUseAcknowledgement } =
    await import("@/composables/use-research-use-acknowledgement");
  const a = useResearchUseAcknowledgement();
  const b = useResearchUseAcknowledgement();
  a.acknowledge();
  expect(b.acknowledged.value).toBe(true);
});

test("still works for this page when storage throws", async () => {
  vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
    throw new Error("blocked");
  });
  vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
    throw new Error("blocked");
  });
  const { acknowledged, acknowledge } = await load();
  expect(acknowledged.value).toBe(false);
  expect(() => acknowledge()).not.toThrow();
  expect(acknowledged.value).toBe(true);
});
