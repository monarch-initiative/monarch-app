import { beforeEach, describe, expect, test } from "vitest";
import { useBiolinkModel } from "@/composables/use-biolink-model";

/** biolink slots are keyed by space-separated names, with is_a naming the parent */
const fakeModel = {
  slots: {
    treats: {
      description: "the subject treats the object",
      is_a: "treats or applied or studied to treat",
    },
    "treats or applied or studied to treat": {
      description: "broader treatment relationship",
      is_a: "related to",
    },
    "related to": { description: "a generic relationship" },
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

  test("returns [] for a leaf predicate", async () => {
    const { loadBiolinkModel, getPredicateChildren } = useBiolinkModel();
    await loadBiolinkModel();
    expect(getPredicateChildren("biolink:treats")).toEqual([]);
  });
});
