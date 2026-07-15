import { computed, ref, watch } from "vue";
import { hasClinGenDiseaseAssociation } from "@/api/associations";
import type { ExpandedCurie, Node } from "@/api/model";
import type { BrandKey } from "@/util/linkout";

const RESOURCE_DEFS = [
  {
    prefix: "OMIM:",
    label: "OMIM",
    tooltip:
      "Online Mendelian Inheritance in Man: A curated catalog of human genes, variants, and genetic phenotypes—primarily for clinicians and researchers.",
  },
  {
    prefix: "NORD:",
    label: "NORD",
    tooltip:
      "National Organization for Rare Disorders: Lay-friendly rare disease summaries, advocacy resources, and support services—for patients, families, and healthcare providers",
  },
  {
    prefix: "GARD:",
    label: "GARD",
    tooltip:
      "Genetic and Rare Diseases Information Center: health information on genetic and rare conditions—for patients, caregivers, and providers seeking plain-language guidance.",
  },
  {
    prefix: "Orphanet:",
    label: "ORPHANET",
    tooltip:
      "Orphanet: European reference portal on rare diseases and orphan drugs with disease pages, epidemiology, coding, and expert centers—for clinicians, researchers, policymakers, and patient communities.",
  },
  {
    prefix: "MEDGEN:",
    label: "MEDGEN",
    tooltip:
      "Medical Genetics: NCBI’s structured knowledge base linking diseases, phenotypes, genes, and clinical resources—for clinical geneticists, informaticians, and researchers",
  },
] as const;

const RESOURCE_PREFIXES = RESOURCE_DEFS.map((rec) => rec.prefix);

// ClinGen curates conditions by Mondo ID, so any Mondo disease has a
// corresponding ClinGen condition page keyed on the node's own id.
const CLINGEN_TOOLTIP =
  "ClinGen (Clinical Genome Resource): NIH-funded resource defining the clinical relevance of genes and variants for precision medicine and research. ClinGen curates conditions by Mondo ID.";
const CLINGEN_CONDITION_URL =
  "https://search.clinicalgenome.org/kb/conditions/";

// helper: does an id start with any clinical prefix?
const isClinicalId = (id: string) =>
  RESOURCE_PREFIXES.some((pre) => id.startsWith(pre));

export type ClinicalResourceEntry = {
  id: string;
  url: string;
  label: string;
  source: "external" | "mapping";
  tooltip?: string;
  // explicit brand override for entries whose id prefix doesn't map to a brand
  // (e.g. ClinGen, keyed on a MONDO id)
  brand?: BrandKey;
};

export function useClinicalResources(node: Node) {
  // ClinGen only has a populated condition page for a fraction of Mondo
  // diseases, so only show the chip once we've confirmed it actually has
  // gene-to-disease or variant-to-disease evidence for this exact id. Fails
  // closed (chip hidden) if the check errors, since a bad linkout is worse
  // than a missing chip.
  const hasClinGenData = ref(false);
  watch(
    () => node.id,
    (id) => {
      hasClinGenData.value = false;
      if (!id?.startsWith("MONDO:")) return;
      hasClinGenDiseaseAssociation(id)
        .then((has) => {
          if (id === node.id) hasClinGenData.value = has;
        })
        .catch(() => {});
    },
    { immediate: true },
  );

  const clinicalResources = computed<ClinicalResourceEntry[]>(() => {
    const out: ClinicalResourceEntry[] = [];
    for (const { prefix, label, tooltip } of RESOURCE_DEFS) {
      const ext = node.external_links?.find((link: ExpandedCurie) =>
        link.id.startsWith(prefix),
      );
      if (ext) {
        out.push({
          id: ext.id,
          url: ext.url || "",
          label,
          source: "external",
          tooltip,
        });
        continue;
      }
      const map = node.mappings?.find((item: ExpandedCurie) =>
        item.id.startsWith(prefix),
      );
      if (map) {
        out.push({
          id: map.id,
          url: map.url || "",
          label,
          source: "mapping",
          tooltip,
        });
      }
    }
    // ClinGen link is derived from the disease's own Mondo id rather than from
    // external_links/mappings, so add it once we've confirmed ClinGen has
    // data for this id.
    if (hasClinGenData.value) {
      out.push({
        id: node.id,
        url: `${CLINGEN_CONDITION_URL}${node.id}`,
        label: "ClinGen",
        source: "external",
        tooltip: CLINGEN_TOOLTIP,
        brand: "clingen",
      });
    }
    return out;
  });

  // mappings not in clinical set
  const otherMappings = computed(
    () => node.mappings?.filter((mapping) => !isClinicalId(mapping.id)) || [],
  );

  // external refs not in clinical set
  const externalRefs = computed<ExpandedCurie[]>(
    () => node.external_links?.filter((link) => !isClinicalId(link.id)) || [],
  );

  return { clinicalResources, otherMappings, externalRefs };
}
