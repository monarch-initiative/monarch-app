import { expect, test } from "vitest";
import { parseRetrievalSources } from "@/util/retrievalSources";

test("parses a MEDIC-style nested retrieval-source chain", () => {
  /** the API serializes `sources` as a list holding one JSON-encoded array */
  const sources = [
    JSON.stringify([
      {
        resource_id: "infores:medic",
        resource_role: "primary_knowledge_source",
        upstream_resource_ids: ["infores:dailymed"],
      },
      {
        resource_id: "infores:dailymed",
        resource_role: "supporting_data_source",
        upstream_resource_ids: null,
      },
    ]),
  ];
  const parsed = parseRetrievalSources(sources);
  expect(parsed).toHaveLength(2);
  expect(parsed[0].resource_id).toBe("infores:medic");
  expect(parsed[0].resource_role).toBe("primary_knowledge_source");
  expect(parsed[0].upstream_resource_ids).toEqual(["infores:dailymed"]);
  expect(parsed[1].resource_role).toBe("supporting_data_source");
});

test("returns empty for missing or empty sources", () => {
  expect(parseRetrievalSources(undefined)).toEqual([]);
  expect(parseRetrievalSources(null)).toEqual([]);
  expect(parseRetrievalSources([])).toEqual([]);
});

test("falls back to a bare resource_id for plain CURIE strings", () => {
  /** if `sources` is delivered as plain CURIEs rather than JSON, keep them */
  const parsed = parseRetrievalSources([
    "infores:medic",
    JSON.stringify([{ resource_id: "infores:ctd" }]),
  ]);
  expect(parsed).toHaveLength(2);
  expect(parsed[0].resource_id).toBe("infores:medic");
  expect(parsed[1].resource_id).toBe("infores:ctd");
});

test("drops empty entries without throwing", () => {
  const parsed = parseRetrievalSources(["", JSON.stringify(null)]);
  expect(parsed).toEqual([]);
});
