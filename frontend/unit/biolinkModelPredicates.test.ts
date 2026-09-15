import { beforeEach, describe, expect, test } from "vitest";
import { useBiolinkModel } from "@/composables/use-biolink-model";

/** biolink slots are keyed by space-separated names, with is_a naming the parent */
const fakeModel = {
  slots: {
    treats: {
      description: "the subject treats the object",
      is_a: "treats or applied or studied to treat",
      aliases: ["therapeutic"],
    },
    "treats or applied or studied to treat": {
      description: "broader treatment relationship",
      is_a: "related to",
    },
    "related to": { description: "a generic relationship" },
    // biolink attaches these to "treats" via mixins, not is_a
    "ameliorates condition": {
      description: "improves a condition",
      is_a: "affects",
      mixins: ["treats"],
    },
    "preventative for condition": {
      description: "reduces the likelihood of a condition",
      is_a: "affects likelihood of",
      mixins: ["treats"],
    },
  },
};

beforeEach(() => {
  // reset the module-level singleton so each test loads the fake model fresh
  useBiolinkModel().clearCache();
  localStorage.setItem("biolink-model-cache", JSON.stringify(fakeModel));
  localStorage.setItem("biolink-model-cache-timestamp", Date.now().toString());
});

describe("getPredicateAncestors", () => {
  test("walks the is_a chain from the most specific parent outward", async () => {
    const { loadBiolinkModel, getPredicateInfo, getPredicateAncestors } =
      useBiolinkModel();
    await loadBiolinkModel();

    expect(getPredicateInfo("biolink:treats")?.description).toBe(
      "the subject treats the object",
    );
    expect(getPredicateAncestors("biolink:treats").map((a) => a.name)).toEqual([
      "treats or applied or studied to treat",
      "related to",
    ]);
  });

  test("respects the depth limit", async () => {
    const { loadBiolinkModel, getPredicateAncestors } = useBiolinkModel();
    await loadBiolinkModel();
    expect(
      getPredicateAncestors("biolink:treats", 1).map((a) => a.name),
    ).toEqual(["treats or applied or studied to treat"]);
  });

  test("returns [] for an unknown predicate", async () => {
    const { loadBiolinkModel, getPredicateAncestors } = useBiolinkModel();
    await loadBiolinkModel();
    expect(getPredicateAncestors("biolink:does_not_exist")).toEqual([]);
  });

  test("terminates on an is_a cycle without looping", async () => {
    const { clearCache, loadBiolinkModel, getPredicateAncestors } =
      useBiolinkModel();
    clearCache();
    localStorage.setItem(
      "biolink-model-cache",
      JSON.stringify({
        slots: {
          a: { description: "a", is_a: "b" },
          b: { description: "b", is_a: "a" },
        },
      }),
    );
    localStorage.setItem(
      "biolink-model-cache-timestamp",
      Date.now().toString(),
    );
    await loadBiolinkModel();
    // b -> a, then a -> b is already seen, so it stops
    expect(getPredicateAncestors("biolink:a").map((x) => x.name)).toEqual([
      "b",
      "a",
    ]);
  });
});

describe("getPredicateInfo", () => {
  test("resolves a predicate by alias", async () => {
    const { loadBiolinkModel, getPredicateInfo } = useBiolinkModel();
    await loadBiolinkModel();
    expect(getPredicateInfo("biolink:therapeutic")?.description).toBe(
      "the subject treats the object",
    );
  });
});

describe("getPredicateChildren", () => {
  test("finds direct children (slots whose is_a is this predicate)", async () => {
    const { loadBiolinkModel, getPredicateChildren } = useBiolinkModel();
    await loadBiolinkModel();
    expect(
      getPredicateChildren("biolink:related_to").map((c) => c.name),
    ).toEqual(["treats or applied or studied to treat"]);
    expect(
      getPredicateChildren("biolink:treats_or_applied_or_studied_to_treat").map(
        (c) => c.name,
      ),
    ).toEqual(["treats"]);
  });

  test("finds mixin children (e.g. treats -> ameliorates/preventative)", async () => {
    const { loadBiolinkModel, getPredicateChildren } = useBiolinkModel();
    await loadBiolinkModel();
    expect(getPredicateChildren("biolink:treats").map((c) => c.name)).toEqual([
      "ameliorates condition",
      "preventative for condition",
    ]);
  });

  test("returns [] for a leaf predicate", async () => {
    const { loadBiolinkModel, getPredicateChildren } = useBiolinkModel();
    await loadBiolinkModel();
    expect(getPredicateChildren("biolink:ameliorates_condition")).toEqual([]);
  });
});
