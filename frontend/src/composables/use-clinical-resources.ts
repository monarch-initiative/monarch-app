import { computed } from "vue";
import type { ExpandedCurie, Node } from "@/api/model";

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

// helper: does an id start with any clinical prefix?
const isClinicalId = (id: string) =>
  RESOURCE_PREFIXES.some((pre) => id.startsWith(pre));

export type ResourceEntry = {
  id: string;
  url: string;
  label: string;
  source: "external" | "mapping";
  tooltip?: string;
};

export function useClinicalResources(node: Node) {
  const clinicalResources = computed<ResourceEntry[]>(() => {
    const out: ResourceEntry[] = [];
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
