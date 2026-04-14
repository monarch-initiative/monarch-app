import { describe, expect, test } from "vitest";
import {
  AGENT_TYPE_KEYS,
  AGENT_TYPE_META,
  formatAgentType,
  getAgentTypeMeta,
} from "@/util/agentType";

describe("getAgentTypeMeta", () => {
  test("returns correct metadata for known keys", () => {
    const meta = getAgentTypeMeta("manual_agent");
    expect(meta.icon).toBe("user");
    expect(meta.label).toBe("Manual Agent");
    expect(meta.description).toContain("human agent");
  });

  test("returns correct metadata for automated_agent", () => {
    const meta = getAgentTypeMeta("automated_agent");
    expect(meta.icon).toBe("robot");
    expect(meta.label).toBe("Automated Agent");
  });

  test("returns fallback for unknown keys", () => {
    const meta = getAgentTypeMeta("completely_unknown_type");
    expect(meta.icon).toBe("circle-question");
    expect(meta.label).toBe("Unknown");
    expect(meta.description).toBe("Unrecognized agent type");
  });

  test("returns not_provided metadata for not_provided key", () => {
    const meta = getAgentTypeMeta("not_provided");
    expect(meta.label).toBe("Not Provided");
  });
});

describe("formatAgentType", () => {
  test("returns human-readable label for known keys", () => {
    expect(formatAgentType("manual_agent")).toBe("Manual Agent");
    expect(formatAgentType("text_mining_agent")).toBe("Text Mining Agent");
  });

  test("returns fallback label for unknown keys", () => {
    expect(formatAgentType("something_else")).toBe("Unknown");
  });
});

describe("AGENT_TYPE_KEYS", () => {
  test("contains all keys from AGENT_TYPE_META", () => {
    expect(AGENT_TYPE_KEYS).toEqual(Object.keys(AGENT_TYPE_META));
  });

  test("includes expected entries", () => {
    expect(AGENT_TYPE_KEYS).toContain("manual_agent");
    expect(AGENT_TYPE_KEYS).toContain("automated_agent");
    expect(AGENT_TYPE_KEYS).toContain("not_provided");
  });
});
