import { expect, test } from "vitest";
import { mergeArrays } from "@/util/object";

const arrayA = [
  { id: "abc", animal: "cat" },
  { id: "123", animal: "dog" },
];

const arrayB = [
  { id: "abc", color: "red" },
  { id: "def", color: "green" },
  { id: "456", color: "blue" },
];

/** check that two arrays contain same entries, irrespective of order */
const compareSets = (setA: Iterable<unknown>, setB: Iterable<unknown>) =>
  expect(new Set(setA)).toStrictEqual(new Set(setB));

test("Merge arrays works", () => {
  compareSets(mergeArrays(arrayA, arrayB), [
    { id: "abc", animal: "cat", color: "red" },
    { id: "123", animal: "dog" },
    { id: "def", color: "green" },
    { id: "456", color: "blue" },
  ]);
  compareSets(mergeArrays(arrayA, arrayB, true), [
    { id: "abc", animal: "cat", color: "red" },
    { id: "123", animal: "dog" },
  ]);
});
