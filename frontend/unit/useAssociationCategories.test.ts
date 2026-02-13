import { describe, expect, it } from "vitest";
import { useAssociationCategories } from "@/composables/use-association-categories";

type AssocCount = { category?: string; label: string; count: number };
type TestNode = { association_counts?: AssocCount[] };

const hidden =
  "biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation";
const causal = "biolink:CausalGeneToDiseaseAssociation";
const genePh = "biolink:GeneToPhenotypicFeatureAssociation";

describe("useAssociationCategories", () => {
  it("returns [] when association_counts is missing", () => {
    const node: TestNode = {};
    const { options } = useAssociationCategories(node as any);
    expect(options.value).toEqual([]);
  });

  it("maps to {id,label,count} and startCases the label", () => {
    const node: TestNode = {
      association_counts: [{ category: "X", label: "hello world", count: 3 }],
    };
    const { options } = useAssociationCategories(node as any);
    expect(options.value).toEqual([
      { id: "X", label: "Hello World", count: 3 },
    ]);
  });

  it("filters out hidden categories", () => {
    const node: TestNode = {
      association_counts: [
        { category: hidden, label: "should hide", count: 1 },
        { category: "Y", label: "keep me", count: 2 },
      ],
    };
    const { options } = useAssociationCategories(node as any);
    expect(options.value.map((o) => o.id)).toEqual(["Y"]);
  });

  it("keeps special order: causal before gene→phenotype", () => {
    // causal appears after genePh initially → should be moved before
    const node: TestNode = {
      association_counts: [
        {
          category: genePh,
          label: "gene to phenotypic feature association",
          count: 5,
        },
        {
          category: causal,
          label: "causal gene to disease association",
          count: 2,
        },
      ],
    };
    const { options } = useAssociationCategories(node as any);
    expect(options.value.map((o) => o.id)).toEqual([causal, genePh]);
  });

  it("does not reorder if one of the two categories is missing", () => {
    const node: TestNode = {
      association_counts: [
        {
          category: genePh,
          label: "gene to phenotypic feature association",
          count: 5,
        },
        { category: "Z", label: "other", count: 1 },
      ],
    };
    const { options } = useAssociationCategories(node as any);
    expect(options.value.map((o) => o.id)).toEqual([genePh, "Z"]);
  });

  it("handles missing category by substituting empty id", () => {
    const node: TestNode = {
      association_counts: [{ category: undefined, label: "no id", count: 1 }],
    };
    const { options } = useAssociationCategories(node as any);
    expect(options.value[0]).toMatchObject({ id: "", count: 1 });
  });
});
