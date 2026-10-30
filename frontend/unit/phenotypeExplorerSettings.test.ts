import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { ApiError } from "@/api";
import {
  cleanSettings,
  compareSetToGroup,
  compareSetToSet,
} from "@/api/phenotype-explorer";

const mockFetch = vi.fn();

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
});

afterEach(() => {
  vi.unstubAllGlobals();
  mockFetch.mockReset();
});

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });

/** body of the request fetch was last called with */
const sentBody = () => {
  const [, options] = mockFetch.mock.calls.at(-1) as [unknown, RequestInit];
  return JSON.parse(String(options.body));
};

/** search result for an entity with the given scores */
const result = (id: string, score: number, s2o: number, o2s: number) => ({
  subject: { id, name: id, category: "biolink:Disease" },
  score,
  subject_to_object_score: s2o,
  object_to_subject_score: o2s,
  similarity: {
    object_termset: { "HP:1": { id: "HP:1", label: "one" } },
    object_best_matches: {
      "HP:1": {
        match_target: "HP:2",
        match_target_label: "two",
        score,
        similarity: { ancestor_id: "HP:1", jaccard_similarity: 0.5 },
      },
    },
  },
});

describe("cleanSettings", () => {
  test("drops defaults, so untouched requests send nothing new", () => {
    expect(
      cleanSettings({
        directionality: "bidirectional",
        search_mode: "hybrid",
        information_content: "ontology",
        tie_break: "none",
      }),
    ).toEqual({});
  });

  test("keeps changed settings and drops unknown values", () => {
    expect(
      cleanSettings({
        directionality: "object_to_subject",
        search_mode: "fulll",
        tie_break: "frequency",
        unknown: "x",
      }),
    ).toEqual({ directionality: "object_to_subject", tie_break: "frequency" });
  });

  test("keeps a known corpus only with annotation information content", () => {
    expect(
      cleanSettings({
        information_content: "annotation",
        group: "Human Diseases",
      }),
    ).toEqual({ information_content: "annotation", group: "Human Diseases" });
    expect(
      cleanSettings({
        information_content: "ontology",
        group: "Human Diseases",
      }),
    ).toEqual({});
    expect(
      cleanSettings({ information_content: "annotation", group: "Martians" }),
    ).toEqual({ information_content: "annotation" });
  });
});

describe("compareSetToGroup", () => {
  /** api order: B and C tie, A highest */
  const response = [
    result("A", 3, 3.5, 2.5),
    result("B", 2, 1, 3),
    result("C", 2, 2, 2),
  ];

  test("without a tie-break, ranks ties as before", async () => {
    mockFetch.mockResolvedValueOnce(json(response));
    const { summary } = await compareSetToGroup(
      ["HP:1"],
      "Human Diseases",
      "ancestor_information_content",
      {},
    );
    expect(summary.map(({ subject }) => subject.id)).toEqual(["A", "C", "B"]);
    expect(sentBody()).toEqual({
      termset: ["HP:1"],
      group: "Human Diseases",
      metric: "ancestor_information_content",
    });
  });

  test("with a tie-break, keeps the api's order of ties", async () => {
    mockFetch.mockResolvedValueOnce(json(response));
    const { summary } = await compareSetToGroup(
      ["HP:1"],
      "Human Diseases",
      "ancestor_information_content",
      { tie_break: "frequency" },
    );
    expect(summary.map(({ subject }) => subject.id)).toEqual(["A", "B", "C"]);
    expect(sentBody().tie_break).toBe("frequency");
  });

  test("carries both direction scores", async () => {
    mockFetch.mockResolvedValueOnce(json(response));
    const { summary } = await compareSetToGroup(["HP:1"], "Human Diseases");
    expect(summary[0]).toMatchObject({
      subjectToObjectScore: 3.5,
      objectToSubjectScore: 2.5,
    });
  });

  test("passes on the reason the api refused a request", async () => {
    mockFetch.mockResolvedValueOnce(
      json({ detail: "No annotation IC for corpus x" }, 400),
    );
    const error = await compareSetToGroup(["HP:1"], "Human Diseases").catch(
      (caught) => caught,
    );
    expect(error).toBeInstanceOf(ApiError);
    expect(error.detail).toBe("No annotation IC for corpus x");
  });
});

describe("compareSetToSet", () => {
  test("averages each direction, unmatched phenotypes counting as 0", async () => {
    mockFetch.mockResolvedValueOnce(
      json({
        subject_termset: {
          "HP:1": { id: "HP:1", label: "one" },
          "HP:2": { id: "HP:2", label: "two" },
        },
        object_termset: { "HP:3": { id: "HP:3", label: "three" } },
        subject_best_matches: {
          "HP:1": {
            match_source: "HP:1",
            match_target: "HP:3",
            score: 4,
            similarity: {},
          },
        },
        object_best_matches: {
          "HP:3": {
            match_source: "HP:3",
            match_target: "HP:1",
            score: 4,
            similarity: {},
          },
        },
      }),
    );
    const { subjectAverage, objectAverage } = await compareSetToSet(
      ["HP:1", "HP:2"],
      ["HP:3"],
    );
    expect(subjectAverage).toBe(2);
    expect(objectAverage).toBe(4);
  });
});
