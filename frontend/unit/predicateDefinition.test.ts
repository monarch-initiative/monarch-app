import { describe, expect, test } from "vitest";
import {
  predicateDocsUrl,
  predicateLabel,
} from "@/composables/use-predicate-definition";

describe("predicate formatting", () => {
  test.each([
    ["biolink:applied_to_treat", "applied to treat"],
    ["applied to treat", "applied to treat"],
    ["biolink:treats", "treats"],
    [undefined, ""],
  ])("label(%s) -> %s", (input, expected) => {
    expect(predicateLabel(input)).toBe(expected);
  });

  test.each([
    // a CURIE, as the detail views pass it
    ["biolink:applied_to_treat", "applied_to_treat"],
    // a biolink slot key, as the hierarchy passes it -- these are space-separated
    ["applied to treat", "applied_to_treat"],
    [
      "treats or applied or studied to treat",
      "treats_or_applied_or_studied_to_treat",
    ],
  ])("docsUrl(%s) slugs to %s", (input, slug) => {
    expect(predicateDocsUrl(input)).toBe(
      `https://biolink.github.io/biolink-model/${slug}/`,
    );
  });

  test("both separators reach the same page", () => {
    // The two builders this replaced each handled only one separator, so a slot key
    // and its CURIE produced different URLs and one of them 404'd.
    expect(predicateDocsUrl("biolink:applied_to_treat")).toBe(
      predicateDocsUrl("applied to treat"),
    );
  });
});
