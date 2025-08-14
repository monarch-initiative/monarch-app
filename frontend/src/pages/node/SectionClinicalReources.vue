<template>
  <AppDetail
    v-if="clinicalResources?.length"
    title="Patient and Clinical Resources"
    :full="true"
  >
    <div class="clinical-resources">
      <div class="custom-grid">
        <div v-for="(res, id) in clinicalResources" :key="id" class="linkout">
          <AppLink
            :to="res.url || ''"
            class="brand-chip"
            :style="chipStyle(res)"
            :aria-label="res.label || res.id"
            v-tooltip="tipText(res)"
          >
            <span class="brand-wordmark">{{
              brandText(res.id, res.label)
            }}</span>
          </AppLink>
          <!-- removed the bottom ID display -->
        </div>
      </div>

      <div class="sub-items">
        <div v-if="nodeInheritance">
          <span class="info-label"> Heritability : </span>
          <AppLink
            v-tooltip="nodeInheritance?.name"
            :to="nodeInheritance?.id || ''"
            >{{ nodeInheritance?.name }}</AppLink
          >
        </div>

        <div v-if="casualGenes?.length">
          <span class="info-label"> Casual Genes : </span>
          <AppNodeBadge
            v-for="(gene, index) in casualGenes"
            :key="index"
            :node="omit(gene, 'in_taxon_label')"
          />
        </div>

        <div>
          <span class="info-label"> Frequency : </span>
          <span>{{ frequencyLabel }}</span>
        </div>
      </div>
    </div>
  </AppDetail>
</template>

<script setup lang="ts">
import { omit } from "lodash";
import type { Entity, Node as ModelNode } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppLink from "@/components/AppLink.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import { useClinicalResources } from "@/composables/use-clinical-resources";
import { BRAND_STYLES, brandFromId } from "@/util/linkout";

type ClinicalResource = {
  id: string;
  url?: string;
  label?: string;
  /** dynamic overrides coming from API */
  bg?: string;
  fg?: string;
  border?: string;
  tooltip?: string;
};

type Props = {
  clinicalSynopsis?: { id: string; url?: string }[];
  infoForPatients?: { id: string; url?: string }[];
  nodeInheritance?: Entity;
  casualGenes?: Entity[];
  frequencyLabel?: "Rare" | "Common";
  node: ModelNode;
};

const props = defineProps<Props>();
const { clinicalResources } = useClinicalResources(props.node);

const chipStyle = (res: ClinicalResource) => {
  const k = brandFromId(res.id);
  const s = k ? BRAND_STYLES[k] : null;
  return {
    "--brand-bg": s?.bg ?? "#666",
    "--brand-fg": s?.fg ?? "#FFFFFF", // ← text color from brand map
    "--brand-border": s?.border ?? "#444",
    fontFamily: s?.font ?? "system-ui, Segoe UI, Roboto, Arial, sans-serif", // ← font from brand map
    textTransform: s?.transform ?? "none",
    letterSpacing: s?.letterSpacing ?? "0.01em",
    fontWeight: s?.weight ?? 700,
  } as Record<string, string | number>;
};

const brandText = (id: string, fallback?: string) => {
  const k = brandFromId(id);
  return k ? BRAND_STYLES[k].label : fallback || id.split(":")[0];
};

const tipText = (res: ClinicalResource) => {
  const desc = res.tooltip ?? res.label ?? "";
  return desc ? `${res.id} - ${desc}` : res.id;
};
</script>

<style lang="scss" scoped>
.custom-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  padding: 1em 1em;
  gap: 1.25em;
}

.linkout {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35em;
}

.brand-chip {
  /* base color comes from chipStyle → --brand-bg */
  --bg-base: var(--brand-bg);

  /* default = slightly lighter than brand; hover = a bit closer to brand */
  --bg-lite: color-mix(in srgb, var(--bg-base) 80%, white); /* 20% white */
  --bg-hover: color-mix(in srgb, var(--bg-base) 90%, white); /* 10% white */
  --bd-col: color-mix(in srgb, var(--bg-base) 70%, black);

  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 4.5rem;
  min-height: 1.25rem;
  padding: 0.6rem 1rem;
  border-radius: 12px;
  background: var(--bg-lite);
  box-shadow: 0 16px 38px rgba(16, 24, 40, 0.12);
  color: var(--brand-fg);

  font-size: 1rem;
  text-decoration: none;
  transition:
    background-color 120ms ease,
    border-color 120ms ease,
    transform 120ms ease,
    box-shadow 120ms ease;
}

.brand-chip:hover,
.brand-chip:focus {
  transform: translateY(-1px);
  border-color: color-mix(in srgb, var(--bg-base) 80%, black);
  background: var(--bg-hover);
  box-shadow: 0 6px 18px rgba(16, 24, 40, 0.12);
}

.clinical-resources {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
  padding: 0.5em 0em;
  gap: 0.2em;
  background-color: #f7fbfe;
}

.sub-items {
  display: flex;
  flex-direction: column;
  padding-left: 1em;
  gap: 0.5em;
}
/* removed .brand-id entirely */
</style>
