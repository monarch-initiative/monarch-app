// src/composables/useClinicalResources.ts
import { computed } from "vue";
import type { ExpandedCurie, Node } from "@/api/model";

const RESOURCE_DEFS = [
  { prefix: "OMIM:", icon: "omim.png" },
  { prefix: "NORD:", icon: "nord.png" },
  { prefix: "GARD:", icon: "gard.png" },
  { prefix: "Orphanet:", icon: "orphanet.png" },
  { prefix: "MEDGEN:", icon: "medgen.png" },
] as const;

export type ResourceEntry = {
  id: string;
  url: string;
  icon: string;
  source: "external" | "mapping";
};

export function useClinicalResources(node: Node) {
  const clinicalResources = computed<ResourceEntry[]>(() => {
    const out: ResourceEntry[] = [];
    for (const { prefix, icon } of RESOURCE_DEFS) {
      const ext = node.external_links?.find((l: ExpandedCurie) =>
        l.id.startsWith(prefix),
      );
      if (ext) {
        out.push({ id: ext.id, url: ext.url || "", icon, source: "external" });
        continue;
      }
      const map = node.mappings?.find((m: ExpandedCurie) =>
        m.id.startsWith(prefix),
      );
      if (map) {
        out.push({ id: map.id, url: map.url || "", icon, source: "mapping" });
      }
    }
    return out;
  });

  return { clinicalResources };
}
