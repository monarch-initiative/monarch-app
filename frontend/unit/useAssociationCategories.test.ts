import { describe, expect, it } from "vitest";
import { useAssociationCategories } from "@/composables/use-association-categories";

type AssocCount = {
  key?: string;
  category?: string;
  label: string;
  count: number;
};
type TestNode = { association_counts?: AssocCount[] };

const drugIndications =
  "biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation";
const causal = "biolink:CausalGeneToDiseaseAssociation";
const genePh = "biolink:GeneToPhenotypicFeatureAssociation";

describe("useAssociationCategories", () => {
  it("returns [] when association_counts is missing", () => {
    const node: TestNode = {};
    const { options } = useAssociationCategories(node as any);
    expect(options.value).toEqual([]);
  });

  it("maps to {id,category,label,count} and startCases the label", () => {
    const node: TestNode = {
      association_counts: [{ category: "X", label: "hello world", count: 3 }],
    };
    const { options } = useAssociationCategories(node as any);
    // `category` rides alongside `id` because the two diverge once a section has its own
    // key; anything keyed on a biolink category must read `category`, not `id`.
    expect(options.value).toEqual([
      { id: "X", category: "X", label: "Hello World", count: 3 },
    ]);
  });

  it("no longer hides the drug-indication category (now shown, keyed on key)", () => {
    const node: TestNode = {
      association_counts: [
        {
          key: "drug_indications",
          category: drugIndications,
          label: "Treatments",
          count: 1,
        },
        { category: "Y", label: "keep me", count: 2 },
      ],
    };
    const { options } = useAssociationCategories(node as any);
    expect(options.value.map((o) => o.id)).toEqual(["drug_indications", "Y"]);
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

  it("prefers the section key over category for the id", () => {
    // several sections can share one category (biolink:Association),
    // distinguished by their key
    const node: TestNode = {
      association_counts: [
        {
          key: "clinical_measurement_correlated_phenotypes",
          category: "biolink:Association",
          label: "Correlated Phenotypes",
          count: 4,
        },
        {
          key: "clinical_measurement_related_chemicals",
          category: "biolink:Association",
          label: "Related Chemicals",
          count: 7,
        },
      ],
    };
    const { options } = useAssociationCategories(node as any);
    expect(options.value.map((o) => o.id)).toEqual([
      "clinical_measurement_correlated_phenotypes",
      "clinical_measurement_related_chemicals",
    ]);
  });
});

test("hides a section by its category even when its key differs", () => {
  /**
   * HIDDEN_CATEGORIES holds biolink categories, but the option id is now a
   * section key. Checking the hidden set against the id worked only while every
   * key equalled its category — the first section with a distinct key (LOINC,
   * MEDIC+CTD) would have silently reappeared.
   */
  const node = {
    association_counts: [
      {
        key: "drug_indications",
        category:
          "biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation",
        label: "Medical Action",
        count: 7,
      },
    ],
  } as never;
  expect(useAssociationCategories(node).options.value).toEqual([]);
});

test("keeps a visible section whose key differs from its category", () => {
  const node = {
    association_counts: [
      {
        key: "clinical_measurement_related_anatomy",
        category: "biolink:Association",
        label: "Related Anatomy",
        count: 3,
      },
    ],
  } as never;
  const options = useAssociationCategories(node).options.value;
  expect(options).toHaveLength(1);
  expect(options[0].id).toBe("clinical_measurement_related_anatomy");
  expect(options[0].category).toBe("biolink:Association");
});
