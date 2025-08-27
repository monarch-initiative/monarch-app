import { describe, expect, it } from "vitest";
import type { DirectionalAssociation } from "@/api/model";
import { buildAssociationCols } from "@/pages/node/associationColumns";

type Ctx = Parameters<typeof buildAssociationCols>[0];

const makeRow = (patch: Record<string, any> = {}): DirectionalAssociation =>
  ({
    direction: "outgoing",
    id: "S1-O1",
    subject: "S1",
    subject_label: "Subject",
    subject_category: "biolink:Gene",
    object: "O1",
    object_label: "Object",
    object_category: "biolink:Disease",
    predicate: "biolink:related_to",
    evidence_count: 1,
    primary_knowledge_source: "SourceX",
    original_subject: "S1",
    ...patch,
  }) as any;

const makeCtx = (patch: Partial<Ctx> = {}): Ctx => ({
  categoryId: "biolink:SomeAssociation",
  nodeCategory: "biolink:Gene",
  isDirect: true,
  items: [makeRow()],
  getCategoryLabel: (id) =>
    id === "biolink:Gene" ? "Gene" : id === "biolink:Disease" ? "Disease" : id,
  ...patch,
});

const keys = (cols: Array<{ key?: string; slot?: string }>) =>
  cols.map((c) => c.key ?? c.slot);

describe("buildAssociationCols", () => {
  it("builds base columns with headings derived from first item categories", () => {
    const cols = buildAssociationCols(makeCtx());
    expect(keys(cols).slice(0, 4)).toEqual([
      "subject_label",
      "predicate",
      "object_label",
      "evidence_count",
    ]);
    // headings reflect getCategoryLabel on subject/object categories
    expect(cols[0].heading).toBe("Gene");
    expect(cols[2].heading).toBe("Disease");
  });

  it("adds extra 'Taxon' column for Interaction categories (with divider)", () => {
    const cols = buildAssociationCols(
      makeCtx({ categoryId: "biolink:ProteinProteinInteraction" }),
    );
    // last two entries should be divider then taxon
    const end = cols.slice(-2);
    expect(end[0].slot).toBe("divider");
    expect(end[1].slot).toBe("taxon");
  });

  it("CausalGeneToDiseaseAssociation (Disease, Direct): removes object & predicate; inserts Source before Details", () => {
    const cols = buildAssociationCols(
      makeCtx({
        nodeCategory: "biolink:Disease",
        isDirect: true,
        categoryId: "biolink:CausalGeneToDiseaseAssociation",
      }),
    );
    const k = keys(cols);
    expect(k).not.toContain("object_label");
    expect(k).not.toContain("predicate");
    const iSource = k.indexOf("primary_knowledge_source");
    const iDetails = k.indexOf("evidence_count");
    expect(iSource).toBeGreaterThan(-1);
    expect(iSource).toBeLessThan(iDetails);
  });

  it("VariantToDiseaseAssociation: Direct removes object; always adds Source before Details", () => {
    const direct = buildAssociationCols(
      makeCtx({
        nodeCategory: "biolink:Disease",
        isDirect: true,
        categoryId: "biolink:VariantToDiseaseAssociation",
      }),
    );
    const kd = keys(direct);
    expect(kd).not.toContain("object_label");
    const iSourceD = kd.indexOf("primary_knowledge_source");
    const iDetailsD = kd.indexOf("evidence_count");
    expect(iSourceD).toBeGreaterThan(-1);
    expect(iSourceD).toBeLessThan(iDetailsD);

    const all = buildAssociationCols(
      makeCtx({
        nodeCategory: "biolink:Disease",
        isDirect: false,
        categoryId: "biolink:VariantToDiseaseAssociation",
      }),
    );
    const ka = keys(all);
    expect(ka).toContain("object_label"); // not removed on All
    const iSourceA = ka.indexOf("primary_knowledge_source");
    const iDetailsA = ka.indexOf("evidence_count");
    expect(iSourceA).toBeGreaterThan(-1);
    expect(iSourceA).toBeLessThan(iDetailsA);
  });

  it("Disease + Direct + other categories: removes subject_label and predicate", () => {
    const cols = buildAssociationCols(
      makeCtx({
        nodeCategory: "biolink:Disease",
        isDirect: true,
        categoryId: "biolink:OtherDiseaseAssociation",
      }),
    );
    const k = keys(cols);
    expect(k).not.toContain("subject_label");
    expect(k).not.toContain("predicate");
    expect(k).toContain("object_label");
  });

  it("GenotypeToDiseaseAssociation: removes predicate, ensures Taxon before Subject; adds Source before Details on Direct", () => {
    const cols = buildAssociationCols(
      makeCtx({
        nodeCategory: "biolink:Disease",
        isDirect: true,
        categoryId: "biolink:GenotypeToDiseaseAssociation",
      }),
    );
    const k = keys(cols);
    expect(k).not.toContain("predicate");
    const iTaxon = k.indexOf("taxon");
    const iSubject = k.indexOf("subject_label");
    expect(iTaxon).toBeGreaterThan(-1);
    expect(iTaxon).toBeLessThan(iSubject);
    const iSource = k.indexOf("primary_knowledge_source");
    const iDetails = k.indexOf("evidence_count");
    expect(iSource).toBeGreaterThan(-1);
    expect(iSource).toBeLessThan(iDetails);
  });

  it("DiseaseToPhenotypicFeatureAssociation (Disease, All): swaps subject and object", () => {
    const cols = buildAssociationCols(
      makeCtx({
        nodeCategory: "biolink:Disease",
        isDirect: false,
        categoryId: "biolink:DiseaseToPhenotypicFeatureAssociation",
      }),
    );
    const k = keys(cols);
    const iSub = k.indexOf("subject_label");
    const iObj = k.indexOf("object_label");
    expect(iSub).toBeGreaterThan(-1);
    expect(iObj).toBeGreaterThan(-1);
    expect(iObj).toBeLessThan(iSub);
  });

  it("GeneToPhenotypicFeatureAssociation (Disease, All): drops predicate and adds Disease Context if any row has it", () => {
    const cols = buildAssociationCols(
      makeCtx({
        nodeCategory: "biolink:Disease",
        isDirect: false,
        categoryId: "biolink:GeneToPhenotypicFeatureAssociation",
        items: [makeRow({ disease_context_qualifier: "X" })],
      }),
    );
    const k = keys(cols);
    expect(k).not.toContain("predicate");
    expect(k).toContain("disease_context_qualifier");
    const iCtx = k.indexOf("disease_context_qualifier");
    const iSub = k.indexOf("subject_label");
    expect(iCtx).toBeLessThan(iSub);
  });

  it("PhenotypicFeature categories add Frequency and Onset columns (plus divider)", () => {
    const cols = buildAssociationCols(
      makeCtx({
        categoryId: "biolink:GeneToPhenotypicFeatureAssociation",
        nodeCategory: "biolink:Gene",
        isDirect: true,
      }),
    );
    const k = keys(cols);
    expect(k).toContain("divider");
    expect(k).toContain("frequency_qualifier");
    expect(k).toContain("onset_qualifier_label");
  });

  it("DiseaseToPhenotypicFeature adds 'original_subject' as Source in extra columns", () => {
    const cols = buildAssociationCols(
      makeCtx({
        categoryId: "biolink:DiseaseToPhenotypicFeatureAssociation",
      }),
    );
    expect(keys(cols)).toContain("original_subject");
  });

  it("Header renames for G2P when viewing a Disease node", () => {
    const cols = buildAssociationCols(
      makeCtx({
        nodeCategory: "biolink:Disease",
        categoryId: "biolink:GeneToPhenotypicFeatureAssociation",
      }),
    );
    const byKey = Object.fromEntries(cols.map((c) => [c.key ?? c.slot, c]));
    expect(byKey["subject_label"].heading).toBe("Causal Genes");
    expect(byKey["object_label"].heading).toBe("Causal Gene Phenotypes");
  });
});
