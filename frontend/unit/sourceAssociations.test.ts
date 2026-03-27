import { beforeEach, describe, expect, it, vi } from "vitest";
import { getSourceAssociations } from "@/api/source-associations";

/** mock the api module's request function */
const mockRequest = vi.fn().mockResolvedValue({ items: [], total: 0 });
vi.mock("@/api", () => ({
  apiUrl: "https://example.com/v3/api",
  request: (...args: unknown[]) => mockRequest(...args),
}));

describe("getSourceAssociations", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls the /association endpoint", async () => {
    await getSourceAssociations();
    expect(mockRequest).toHaveBeenCalledTimes(1);
    const [url] = mockRequest.mock.calls[0];
    expect(url).toBe("https://example.com/v3/api/association");
  });

  it("passes primary_knowledge_source when provided", async () => {
    await getSourceAssociations("infores:monarchinitiative");
    const [, params] = mockRequest.mock.calls[0];
    expect(params.primary_knowledge_source).toBe("infores:monarchinitiative");
  });

  it("omits primary_knowledge_source when not provided", async () => {
    await getSourceAssociations();
    const [, params] = mockRequest.mock.calls[0];
    expect(params.primary_knowledge_source).toBeUndefined();
  });

  it("passes offset and limit", async () => {
    await getSourceAssociations(undefined, 20, 50);
    const [, params] = mockRequest.mock.calls[0];
    expect(params.offset).toBe(20);
    expect(params.limit).toBe(50);
  });

  it("passes facet_fields and filter_queries", async () => {
    const facets = ["category", "predicate"];
    const fqs = ['category:"biolink:Association"'];
    await getSourceAssociations(undefined, 0, 20, facets, fqs);
    const [, params] = mockRequest.mock.calls[0];
    expect(params.facet_fields).toEqual(facets);
    expect(params.filter_queries).toEqual(fqs);
  });

  it("formats sort parameter with direction", async () => {
    const sort = { key: "subject_label" as const, direction: "up" as const };
    await getSourceAssociations(undefined, 0, 20, undefined, undefined, sort);
    const [, params] = mockRequest.mock.calls[0];
    expect(params.sort).toBe("subject_label asc");
  });

  it("maps desc sort direction", async () => {
    const sort = { key: "predicate" as const, direction: "down" as const };
    await getSourceAssociations(undefined, 0, 20, undefined, undefined, sort);
    const [, params] = mockRequest.mock.calls[0];
    expect(params.sort).toBe("predicate desc");
  });

  it("remaps frequency_qualifier sort field", async () => {
    const sort = {
      key: "frequency_qualifier" as const,
      direction: "up" as const,
    };
    await getSourceAssociations(undefined, 0, 20, undefined, undefined, sort);
    const [, params] = mockRequest.mock.calls[0];
    expect(params.sort).toBe("frequency_computed_sortable_float asc");
  });

  it("passes search query", async () => {
    await getSourceAssociations(
      undefined,
      0,
      20,
      undefined,
      undefined,
      null,
      "BRCA1",
    );
    const [, params] = mockRequest.mock.calls[0];
    expect(params.query).toBe("BRCA1");
  });

  it("omits search query when empty", async () => {
    await getSourceAssociations(
      undefined,
      0,
      20,
      undefined,
      undefined,
      null,
      "",
    );
    const [, params] = mockRequest.mock.calls[0];
    expect(params.query).toBeUndefined();
  });

  it("always requests json format", async () => {
    await getSourceAssociations();
    const [, params] = mockRequest.mock.calls[0];
    expect(params.format).toBe("json");
  });
});
