import { describe, expect, test } from "vitest";
import {
  getKnowledgeLevelMeta,
  KNOWLEDGE_LEVEL_KEYS,
  KNOWLEDGE_LEVEL_META,
} from "@/util/knowledgeLevel";

describe("getKnowledgeLevelMeta", () => {
  test("returns correct metadata for a curated assertion", () => {
    const meta = getKnowledgeLevelMeta("knowledge_assertion");
    expect(meta.icon).toBe("circle-check");
    expect(meta.label).toBe("Knowledge Assertion");
    expect(meta.description).toContain("asserted");
  });

  test("returns correct metadata for a prediction", () => {
    const meta = getKnowledgeLevelMeta("prediction");
    expect(meta.icon).toBe("chart-bar");
    expect(meta.label).toBe("Prediction");
  });

  test("returns fallback for unknown values", () => {
    const meta = getKnowledgeLevelMeta("completely_unknown_level");
    expect(meta.icon).toBe("circle-question");
    expect(meta.label).toBe("Unknown");
    expect(meta.description).toBe("Unrecognized knowledge level");
  });
});

describe("KNOWLEDGE_LEVEL_META", () => {
  test("every entry has icon, label, and description", () => {
    for (const key of KNOWLEDGE_LEVEL_KEYS) {
      const meta = KNOWLEDGE_LEVEL_META[key];
      expect(meta.icon).toBeTruthy();
      expect(meta.label).toBeTruthy();
      expect(meta.description).toBeTruthy();
    }
  });
});
