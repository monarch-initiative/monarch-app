<template>
  <AppDetail
    :blank="!clinicalResources.length"
    title="Clinical Resources"
    :full="true"
    class="clinical-resources"
  >
    <div class="custom-grid">
      <div v-for="(res, id) in clinicalResources" :key="id">
        <AppLink :to="res.to" :aria-label="res.tooltip">
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

    <AppFlex direction="col" align-h="left" class="sub-items">
      <div v-if="clinicalSynopsis.length">
        <span> Clinical Synopsis :</span>
        <AppLink
          v-for="(mapping, index) in clinicalSynopsis"
          :key="index"
          :to="mapping.url || ''"
        >
          {{ mapping.id }}
        </AppLink>
      </div>

      <div v-if="infoForPatients.length">
        <span> Info for patients : </span>
        <AppLink
          v-for="(mapping, index) in infoForPatients"
          :key="index"
          :to="mapping.url || ''"
        >
          {{ mapping.id }}
        </AppLink>
      </div>

      <div v-if="nodeInheritance">
        <span> Heritability : </span>
        <AppLink
          v-tooltip="nodeInheritance?.name"
          :to="nodeInheritance?.id || ''"
          >{{ nodeInheritance?.name }}</AppLink
        >
      </div>

      <div v-if="casualGenes.length">
        <span> Casual Genes : </span>
        <AppNodeBadge
          v-for="(gene, index) in casualGenes"
          :key="index"
          :node="omit(gene, 'in_taxon_label')"
        />
      </div>

      <div>
        <span> Frequency : </span>
        <span>{{ frequencyLabel }}</span>
      </div>
    </AppFlex>
  </AppDetail>
</template>

<script setup lang="ts">
import AppDetail from "@/components/AppDetail.vue";
import AppLink from "@/components/AppLink.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import { clinicalResources } from "@/data/clinicalResources";

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
};

const props = defineProps<Props>();
</script>
<style lang="scss" scoped>
.custom-grid {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 60em;
  margin: 1em;
  gap: 2em;
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
  flex: 1 1 7em;
  flex-direction: column;
  align-items: center;
  max-width: 100%;
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
}
.sub-items {
  margin-top: 1em;
  margin: 1em 4em;
}
</style>
