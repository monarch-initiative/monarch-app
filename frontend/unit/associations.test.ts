import { beforeEach, describe, expect, it, vi } from "vitest";
import { hasClinGenDiseaseAssociation } from "@/api/associations";

/** mock the api module's request function */
const mockRequest = vi.fn().mockResolvedValue({ total: 0 });
vi.mock("@/api", () => ({
  apiUrl: "https://example.com/v3/api",
  request: (...args: unknown[]) => mockRequest(...args),
}));

describe("hasClinGenDiseaseAssociation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("queries the /association endpoint for this exact entity", async () => {
    await hasClinGenDiseaseAssociation("MONDO:0007947");
    expect(mockRequest).toHaveBeenCalledTimes(1);
    const [url, params] = mockRequest.mock.calls[0];
    expect(url).toBe("https://example.com/v3/api/association");
    expect(params).toMatchObject({
      entity: "MONDO:0007947",
      category: [
        "biolink:CausalGeneToDiseaseAssociation",
        "biolink:VariantToDiseaseAssociation",
      ],
      primary_knowledge_source: "infores:clingen",
      direct: true,
      limit: 0,
    });
  });

  it("returns true when the query finds matching associations", async () => {
    mockRequest.mockResolvedValue({ total: 3 });
    expect(await hasClinGenDiseaseAssociation("MONDO:0007947")).toBe(true);
  });

  it("returns false when the query finds no associations", async () => {
    mockRequest.mockResolvedValue({ total: 0 });
    expect(await hasClinGenDiseaseAssociation("MONDO:0007947")).toBe(false);
  });
});
