// Centralized builder for association table columns.
import type { DirectionalAssociation } from "@/api/model";
import type { Cols } from "@/components/AppTable.vue";

export type Datum = keyof DirectionalAssociation;

export interface ColumnContext {
  /** e.g., "biolink:GeneToPhenotypicFeatureAssociation" */
  categoryId: string;
  /** e.g., "biolink:Disease" (current page node category) */
  nodeCategory: string;
  /** true => direct-only tab; false => inferred/all tab */
  isDirect: boolean;
  /** current rows used for context (labels, presence tests, etc.) */
  items: DirectionalAssociation[];
  /** label resolver already used in the app */
  getCategoryLabel: (idOrDefault: string) => string;
}

/** Build the AppTable columns for an association category. . */
export const buildAssociationCols = (ctx: ColumnContext): Cols<Datum> => {
  const { categoryId, nodeCategory, isDirect, items, getCategoryLabel } = ctx;

  const first = items?.[0];

  // ---- Base columns (always start with these) ----
  let baseCols: Cols<Datum> = [
    {
      slot: "subject",
      key: "subject_label" as Datum,
      heading: getCategoryLabel(first?.subject_category || "Subject"),
      sortable: true,
    },
    {
      slot: "predicate",
      key: "predicate" as Datum,
      heading: "Association",
      sortable: true,
    },
    {
      slot: "object",
      key: "object_label" as Datum,
      heading: getCategoryLabel(first?.object_category || "Object"),
      sortable: true,
    },
    {
      slot: "details",
      key: "evidence_count" as Datum,
      heading: "Details",
      align: "center",
      sortable: true,
    },
  ];
  const isDisease = nodeCategory === "biolink:Disease";
  const isPhenotype = nodeCategory === "biolink:PhenotypicFeature";

  const extraCols: Cols<Datum> = [];

  // ---- Helpers ----
  const hasSlot = (cols: Array<{ slot?: string }>, name: string) =>
    cols.some((c) => c.slot === name);

  const ensureTaxonColumn = () => {
    if (!hasSlot(baseCols as any, "taxon")) {
      const taxonCol = { slot: "taxon", heading: "Taxon" } as any;
      const iSubject = baseCols.findIndex((c) => c.key === "subject_label");
      if (iSubject > -1) baseCols.splice(iSubject, 0, taxonCol);
      else baseCols.unshift(taxonCol);
    }
  };

  // ---- Extra columns driven by category shape ----
  // Interaction categories: add "Taxon"
  if (categoryId.includes("Interaction")) {
    extraCols.push({ slot: "taxon", heading: "Taxon" } as any);
  }
  if (isDisease) {
    // Causal Gene to Disease: gene only on Direct
    if (isDirect && categoryId === "biolink:CausalGeneToDiseaseAssociation") {
      baseCols = baseCols.filter(
        (col) => col.key !== "object_label" && col.key !== "predicate",
      );

      if (
        !baseCols.some((c) => c.key === ("primary_knowledge_source" as Datum))
      ) {
        const sourceCol = {
          slot: "primary_knowledge_source",
          key: "primary_knowledge_source" as Datum,
          heading: "Source",
          sortable: true,
        } as const;
        const iDetails = baseCols.findIndex(
          (c) => c.key === ("evidence_count" as Datum),
        );
        if (iDetails > -1) baseCols.splice(iDetails, 0, sourceCol as any);
        else baseCols.push(sourceCol as any);
      }
    }

    if (categoryId === "biolink:VariantToDiseaseAssociation") {
      if (isDirect) {
        baseCols = baseCols.filter((col) => col.key !== "object_label");
      }

      if (
        !baseCols.some((c) => c.key === ("primary_knowledge_source" as Datum))
      ) {
        const sourceCol = {
          slot: "primary_knowledge_source",
          key: "primary_knowledge_source" as Datum,
          heading: "Source",
          sortable: true,
        } as const;

        // place Source just before Details
        const iDetails = baseCols.findIndex(
          (c) => c.key === ("evidence_count" as Datum),
        );
        if (iDetails > -1) baseCols.splice(iDetails, 0, sourceCol as any);
        else baseCols.push(sourceCol as any);
      }
    }
    // Direct tab for Disease node: hide “object” or “subject+predicate” depending on category
    if (isDirect) {
      if (
        categoryId === "biolink:CorrelatedGeneToDiseaseAssociation" ||
        categoryId === "biolink:GenotypeToDiseaseAssociation"
      ) {
        baseCols = baseCols.filter((col) => col.key !== "object_label");
      } else if (
        categoryId !== "biolink:GeneToPhenotypicFeatureAssociation" &&
        categoryId !== "biolink:CausalGeneToDiseaseAssociation" &&
        categoryId !== "biolink:VariantToDiseaseAssociation"
      ) {
        baseCols = baseCols.filter(
          (col) => col.key !== "subject_label" && col.key !== "predicate",
        );
      }
    }

    // Genotype→Disease tweaks: drop "Association"; add "Taxon"; add "Source" on Direct
    if (categoryId === "biolink:GenotypeToDiseaseAssociation") {
      baseCols = baseCols.filter((c) => c.key !== "predicate"); // remove "Association"
      ensureTaxonColumn();

      if (
        isDirect &&
        !baseCols.some((c) => c.key === "primary_knowledge_source")
      ) {
        const sourceCol = {
          slot: "primary_knowledge_source",
          key: "primary_knowledge_source" as Datum,
          heading: "Source",
          sortable: true,
        };
        const iDetails = baseCols.findIndex((c) => c.key === "evidence_count");
        if (iDetails > -1) baseCols.splice(iDetails, 0, sourceCol);
        else baseCols.push(sourceCol);
      }
    }

    // Always drop "Association" for D2P and G2P
    if (
      categoryId === "biolink:DiseaseToPhenotypicFeatureAssociation" ||
      categoryId === "biolink:GeneToPhenotypicFeatureAssociation"
    ) {
      baseCols = baseCols.filter((col) => col.key !== "predicate");
    }

    // D2P on All tab: swap Disease(subject) and Phenotype(object)
    if (
      categoryId === "biolink:DiseaseToPhenotypicFeatureAssociation" &&
      !isDirect
    ) {
      const iSub = baseCols.findIndex((c) => c.key === "subject_label");
      const iObj = baseCols.findIndex((c) => c.key === "object_label");
      if (iSub > -1 && iObj > -1) {
        const tmp = baseCols[iSub];
        baseCols[iSub] = baseCols[iObj];
        baseCols[iObj] = tmp;
      }
    }

    // G2P on All tab: show "Disease Context" (left of subject) if any row has it
    if (
      categoryId === "biolink:GeneToPhenotypicFeatureAssociation" &&
      !isDirect
    ) {
      const hasAnyDiseaseContext = (items ?? []).some(
        (r) => !!(r as any)?.disease_context_qualifier,
      );
      if (hasAnyDiseaseContext) {
        const diseaseCol = {
          slot: "disease_context",
          key: "disease_context_qualifier" as Datum,
          heading: "Disease Context",
          sortable: true,
        } as const;

        const idxSubject = baseCols.findIndex((c) => c.key === "subject_label");
        if (idxSubject > -1) baseCols.splice(idxSubject, 0, diseaseCol as any);
        else baseCols.unshift(diseaseCol as any);
      }
    }
  }

  if (isPhenotype) {
    if (categoryId === "biolink:DiseaseToPhenotypicFeatureAssociation") {
      baseCols = baseCols.filter((col) => col.key !== "object_label");
    }
    if (
      categoryId === "biolink:DiseaseToPhenotypicFeatureAssociation" ||
      categoryId === "biolink:GeneToPhenotypicFeatureAssociation"
    ) {
      baseCols = baseCols.filter((col) => col.key !== "predicate");
    }
  }
  // Phenotype categories: add frequency + onset
  if (categoryId.includes("PhenotypicFeature")) {
    extraCols.push(
      {
        slot: "frequency",
        key: "frequency_qualifier" as Datum,
        heading: "Frequency",
        sortable: true,
      } as any,
      {
        key: "onset_qualifier_label" as Datum,
        heading: "Onset",
        sortable: true,
      } as any,
    );
  }

  // D2P: include original subject as "Source"
  if (categoryId.includes("DiseaseToPhenotypicFeature")) {
    extraCols.push({
      key: "original_subject" as Datum,
      heading: "Source",
      sortable: true,
    } as any);
  }

  // Header renames for G2P when viewing a Disease node
  if (
    nodeCategory === "biolink:Disease" &&
    categoryId === "biolink:GeneToPhenotypicFeatureAssociation"
  ) {
    const iSub = baseCols.findIndex((col) => col.key === "subject_label");
    if (iSub > -1)
      baseCols[iSub] = { ...baseCols[iSub], heading: "Causal Genes" };

    const iObj = baseCols.findIndex((c) => c.key === "object_label");
    if (iObj > -1)
      baseCols[iObj] = {
        ...baseCols[iObj],
        heading: "Causal Gene Phenotypes",
      };
  }

  // Visual divider between base and extra columns
  if (extraCols.length) (extraCols as any).unshift({ slot: "divider" });

  return [...baseCols, ...extraCols];
};
