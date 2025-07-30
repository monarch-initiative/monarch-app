<template>
  <AppDetail
    :blank="!clinicalResources.length"
    title="Patient and Clinical Resources"
    :full="true"
    class="clinical-resources"
  >
    <div class="custom-grid">
      <div v-for="(res, id) in clinicalResources" :key="id" class="logo">
        <AppLink :to="res.url" :aria-label="res.tooltip">
          <AppIcon
            v-if="res.icon"
            :tooltip="res.tooltip"
            :aria-label="res.tooltip"
            :icon="res.icon"
            class="icon"
          />
        </AppLink>
      </div>
    </div>

    <div class="sub-items">
      <div v-if="clinicalSynopsis.length">
        <span class="info-label"> Clinical Synopsis </span> :
        <AppLink
          v-for="(mapping, index) in clinicalSynopsis"
          :key="index"
          :to="mapping.url || ''"
        >
          {{ mapping.id }}
        </AppLink>
      </div>

      <div v-if="infoForPatients.length">
        <span class="info-label"> Info for patients : </span>
        <AppLink
          v-for="(mapping, index) in infoForPatients"
          :key="index"
          :to="mapping.url || ''"
        >
          {{ mapping.id }}
        </AppLink>
      </div>

      <div v-if="nodeInheritance">
        <span class="info-label"> Heritability : </span>
        <AppLink
          v-tooltip="nodeInheritance?.name"
          :to="nodeInheritance?.id || ''"
          >{{ nodeInheritance?.name }}</AppLink
        >
      </div>

      <div v-if="casualGenes.length">
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
  </AppDetail>
</template>

<script setup lang="ts">
import type { ExpandedCurie, Node as ModelNode } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppLink from "@/components/AppLink.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import { useClinicalResources } from "@/composables/use-clinical-resources";

type Props = {
  /** current node */
  clinicalSynopsis: { id: string; url?: string }[];
  /* Info for patients */
  infoForPatients: { id: string; url?: string }[];
  /** node object */
  nodeInheritance: {
    id: string;
    name: string;
  };
  casualGenes: { id: string; name: string }[];
  frequencyLabel: "Rare" | "Common";
  /** current node */
  node: ModelNode;
};
const props = defineProps<Props>();
const { clinicalResources } = useClinicalResources(props.node);

console.log("clinicalResources", clinicalResources);
</script>
<style lang="scss" scoped>
.custom-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;

  gap: 2rem;
}
.custom-grid img {
  width: auto;
  height: px;
  object-fit: contain;
}
@media (max-width: 1000px) {
  .custom-grid {
    grid-template-rows: repeat(2, auto);
    grid-auto-columns: minmax(7em, 1fr);
    grid-auto-flow: column;
  }
}

@media (max-width: 600px) {
  .custom-grid {
    grid-template-rows: auto;
    grid-template-columns: 1fr;
    grid-auto-flow: row;
  }
}

.custom-grid > * {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  margin-bottom: 1.5rem;
  gap: 3rem;
}
.icon {
  z-index: 2;
  position: relative;
  position: relative;
  width: 10em;
  height: 5em;

  cursor: pointer;
  transition: transform 0.2s ease;

  @media (max-width: 1000px) {
    width: 9em;
    height: 7em;
  }
}

.logo {
  box-sizing: border-box;

  display: flex;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 60px;
  padding: 2px;
}
.logo img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.icon:hover {
  transform: scale(1.08);
}

a:focus,
.icon:focus {
  outline: none;
}

.clinical-resources {
  display: flex;
  flex-direction: column;
  margin: 1rem 0;
  padding: 1.5rem 1.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background-color: #f7fbfe;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.info-label {
  padding: 0.1rem;
  border-radius: 10%;
}

.sub-items {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 1em;
  gap: 0.5em;
  font-size: 0.9em;
}
</style>
