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
