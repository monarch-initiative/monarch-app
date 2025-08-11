<!--
  node page associations section, table mode. all associations.
-->

<template>
  <!-- status -->
  <AppStatus
    v-if="isLoading"
    code="loading"
    class="loading"
    :style="{ minHeight: dynamicMinHeight + 'em' }"
    >Loading tabulated association data</AppStatus
  >
  <AppStatus v-else-if="isError" code="error"
    >Error loading tabulated association data</AppStatus
  >

  <!-- results -->
  <AppTable
    v-else
    id="associations"
    v-model:sort="sort"
    v-model:per-page="perPage"
    v-model:start="start"
    :cols="cols"
    :rows="associations.items"
    :total="associations.total"
    @download="download"
  >
    <!-- ortholog -->
    <template #ortholog="{ row }">
      <AppNodeBadge
        v-if="row.direction === AssociationDirectionEnum.outgoing"
        :node="{
          id: row.object,
          name: row.object_label,
          category: 'biolink:Gene',
          info: row.object_taxon_label,
        }"
        :breadcrumbs="getBreadcrumbs(node, row, 'subject')"
      />

      <AppNodeBadge
        v-if="row.direction === AssociationDirectionEnum.incoming"
        :node="{
          id: row.subject,
          name: row.subject_label,
          category: 'biolink:Gene',
          info: row.subject_taxon_label,
        }"
        :breadcrumbs="getBreadcrumbs(node, row, 'object')"
      />
    </template>

    <!-- subject -->
    <template #subject="{ row }">
      <div class="badgeColumn">
        <AppNodeBadge
          :node="{
            id: row.subject,
            name: row.highlighting?.subject_label?.[0] || row.subject_label,
            category: row.subject_category,
            info: row.subject_taxon_label,
          }"
          :breadcrumbs="getBreadcrumbs(node, row, 'subject')"
          :highlight="true"
        />

        <AppNodeText
          v-if="row?.highlighting?.subject_closure_label?.[0]"
          :text="`Ancestor: ${row.highlighting.subject_closure_label[0]}`"
          class="text-sm"
          :highlight="true"
        />
      </div>
    </template>

    <!-- predicate -->
    <template #predicate="{ row }">
      <AppPredicateBadge :association="row" :highlight="true" />
    </template>

    <!-- maxorelation -->
    <template #maxorelation="{ row }">
      {{ row.original_predicate }}
    </template>

    <!-- object-->
    <template #object="{ row }">
      <div class="badgeColumn">
        <span v-if="row?.negated === true && direct.id === 'true'">
          Does <span class="negated-text">NOT</span> have
        </span>
        <AppNodeBadge
          :node="{
            id: row.object,
            name: row.highlighting?.object_label?.[0] || row.object_label,
            category: row.object_category,
            info: row.object_taxon_label,
          }"
          :breadcrumbs="getBreadcrumbs(node, row, 'object')"
          :highlight="true"
        />
        <AppNodeText
          v-if="row?.highlighting?.object_closure_label?.[0]"
          :text="`Ancestor: ${row.highlighting.object_closure_label[0]}`"
          class="text-sm"
          :highlight="true"
        />
      </div>
    </template>

    <template #extension="{ row }">
      <AppNodeBadge
        v-if="row.subject_specialization_qualifier_label"
        :node="{
          id: row.subject_specialization_qualifier,
          name: row.subject_specialization_qualifier_label,
          category: row.subject_specialization_qualifier_category,
        }"
        :breadcrumbs="getBreadcrumbs(node, row, 'subject')"
      />
      <!-- unfortunate link hardcoding for CHEBI IDs that we don't have in the graph, TODO: replace with prefix expansion in the browser -->
      <span
        v-else-if="row.subject_specialization_qualifier?.startsWith('CHEBI')"
      >
        <AppLink
          :to="
            'http://purl.obolibrary.org/obo/CHEBI_' +
            row.subject_specialization_qualifier.split(':')[1]
          "
        >
          {{ row.subject_specialization_qualifier }}
        </AppLink>
      </span>
      <span v-else>{{ row.subject_specialization_qualifier }}</span>
    </template>

    <template #disease="{ row }">
      <AppNodeBadge
        v-if="row.disease_context_qualifier"
        :node="{
          id: row.disease_context_qualifier,
          name: row.disease_context_qualifier_label,
          category: 'biolink:Disease',
        }"
      />
      <span v-else class="empty">No info</span>
    </template>

    <template #frequency="{ row }">
      <AppPercentage
        v-if="frequencyPercentage(row) != undefined"
        type="bar"
        :percent="frequencyPercentage(row) || 0"
        :tooltip="frequencyTooltip(row)"
      />
      <span v-else class="empty">No info</span>
    </template>

    <template #has_evidence="{ row }">
      <AppLink
        v-for="source in row.has_evidence_links"
        :key="source.id"
        :to="source.url || ''"
        >{{ source.id }}</AppLink
      >
    </template>

    <!-- button to show details -->
    <template #details="{ row }">
      <AppButton text="Details" icon="info-circle" @click="openModal(row)" />
    </template>

    <!-- extra columns -->

    <!-- taxon specific -->
    <template #taxon="{ row }">
      {{
        row.direction === AssociationDirectionEnum.outgoing
          ? row.object_taxon_label
          : row.subject_taxon_label
      }}
    </template>
    <template #disease_context="{ row }">
      <AppNodeBadge
        v-if="row.disease_context_qualifier"
        :node="{
          id: row.disease_context_qualifier,
          name: row.disease_context_qualifier_label,
          category: 'biolink:Disease',
        }"
      />
      <span v-else class="empty">No info</span>
    </template>
    <!-- phenotype specific -->
    <!-- no template needed because info just plain text -->

    <!-- publication specific -->
    <!-- no template needed because info just plain text -->
  </AppTable>

  <TableControls
    id="showControls"
    v-model:per-page="perPage"
    v-model:start="start"
    :rows="associations.items"
    :total="associations.total"
    @download="download"
  />

  <AppModal v-model="showModal" label="Association Details">
    <SectionAssociationDetails
      :node="node"
      :association="selectedAssociation"
    />
  </AppModal>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch, watchEffect } from "vue";
import {
  downloadAssociations,
  getAssociations,
  maxDownload,
} from "@/api/associations";
import { getCategoryLabel } from "@/api/categories";
import {
  AssociationDirectionEnum,
  type DirectionalAssociation,
  type Node,
} from "@/api/model";
import AppModal from "@/components/AppModal.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppNodeText from "@/components/AppNodeText.vue";
import AppPercentage from "@/components/AppPercentage.vue";
import AppPredicateBadge from "@/components/AppPredicateBadge.vue";
import type { Option } from "@/components/AppSelectSingle.vue";
import AppTable from "@/components/AppTable.vue";
import type { Cols, Sort } from "@/components/AppTable.vue";
import { snackbar } from "@/components/TheSnackbar.vue";
import TableControls from "@/components/TheTableContols.vue";
import { useQuery } from "@/composables/use-query";
import { getBreadcrumbs } from "@/pages/node/AssociationsSummary.vue";
import SectionAssociationDetails from "@/pages/node/SectionAssociationDetails.vue";
import { fieldFor, TYPE_CONFIG } from "@/util/type-config";

type Props = {
  /** current node */
  node: Node;
  /** selected association category */
  category: Option;
  /** "true" = direct only, "false" = include subclasses */
  direct: Option;
  /** search string */
  search: string;
};

const props = defineProps<Props>();

const showModal = ref(false);
const selectedAssociation = ref<DirectionalAssociation | null>(null);
const start = ref(0);
const sort = ref<Sort>();
const perPage = ref(5);

const emit = defineEmits<{
  (e: "update:diseaseSubjectLabel", label: string): void;
  (e: "totals", payload: { direct: number; all: number }): void;
  (e: "inferred-label", payload: { categoryId: string; label: string }): void;
}>();

function openModal(association: DirectionalAssociation) {
  selectedAssociation.value = association;
  showModal.value = true;
}

watch(showModal, (newValue) => {
  if (!newValue) {
    selectedAssociation.value = null;
  }
});

type Datum = keyof DirectionalAssociation;

/** Orholog columns */
const orthologColoumns = computed<Cols<Datum>>(() => {
  return [
    {
      slot: "taxon",
      key: "taxon" as Datum,
      heading: "Taxon",
    },
    {
      slot: "ortholog",
      key: "ortholog" as Datum,
      heading: "Ortholog",
    },
    {
      slot: "has_evidence",
      key: "has_evidence" as Datum,
      heading: "Evidence",
    },
    {
      slot: "primary_knowledge_source",
      key: "primary_knowledge_source" as Datum,
      heading: "Source",
    },
    { slot: "divider" },
    {
      slot: "details",
      key: "evidence_count",
      heading: "Details",
      align: "center",
    },
  ];
});

//calculate dynamic min height of table
const dynamicMinHeight = computed(() => {
  const itemHeight = 3.6;
  return perPage.value * itemHeight;
});

const medicalActionCategory =
  "biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation";
const medicalActionColumns = computed<Cols<Datum>>(() => {
  return [
    {
      slot: "subject",
      key: "subject_label",
      heading: "Medical Action",
    },
    {
      slot: "extension",
      key: "subject_specialization_qualifier",
      heading: "Extension",
    },
    {
      slot: "maxorelation",
      key: "original_predicate",
      heading: "MaXO Relation",
    },
    {
      slot: "object",
      key: "object_label",
      heading: "Phenotype",
    },
    {
      slot: "disease",
      key: "disease_context_qualifier_label",
      heading: "Disease Context",
    },
    {
      slot: "details",
      key: "evidence_count",
      heading: "Details",
      align: "center",
    },
  ];
});

/** table columns */
const cols = computed((): Cols<Datum> => {
  if (props.category.id.includes("GeneToGeneHomology")) {
    return orthologColoumns.value;
  } else if (props.category.id == medicalActionCategory) {
    return medicalActionColumns.value;
  }

  /** standard columns, always present */
  let baseCols: Cols<Datum> = [
    {
      slot: "subject",
      key: "subject_label",
      heading: getCategoryLabel(
        associations.value.items[0]?.subject_category || "Subject",
      ),
      sortable: true,
    },
    {
      slot: "predicate",
      key: "predicate",
      heading: "Association",
      sortable: true,
    },
    {
      slot: "object",
      key: "object_label",
      heading: getCategoryLabel(
        associations.value.items[0]?.object_category || "Object",
      ),
      sortable: true,
    },
    {
      slot: "details",
      key: "evidence_count",
      heading: "Details",
      align: "center",
      sortable: true,
    },
  ];

  /** extra, supplemental columns for certain association types */
  let extraCols: Cols<Datum> = [];

  /** taxon column. exists for many categories, so just add if any row has taxon. */
  if (props.category.id.includes("Interaction")) {
    extraCols.push({
      slot: "taxon",
      heading: "Taxon",
    });
  }

  if (props.direct.id === "true") {
    // CorrelatedGene & Desease model: keep subject_label & predicate, only drop object_label
    if (
      props.category.id === "biolink:CorrelatedGeneToDiseaseAssociation" ||
      props.category.id === "biolink:GenotypeToDiseaseAssociation"
    ) {
      baseCols = baseCols.filter((col) => col.key !== "object_label");
    }
    //  All other direct‐only cases (except Gene-Phenotype): drop subject_label & predicate
    else if (
      props.category.id !== "biolink:GeneToPhenotypicFeatureAssociation"
    ) {
      baseCols = baseCols.filter(
        (col) => col.key !== "subject_label" && col.key !== "predicate",
      );
    }
  }

  if (
    props.node.in_taxon_label == "Homo sapiens" &&
    props.category.id.includes("GeneToPhenotypicFeature")
  ) {
    extraCols.push({
      slot: "disease_context",
      key: "disease_context_qualifier",
      heading: "Disease Context",
      sortable: true,
    });
  }
  /** phenotype specific columns */
  if (props.category.id.includes("PhenotypicFeature")) {
    extraCols.push(
      {
        slot: "frequency",
        key: "frequency_qualifier",
        heading: "Frequency",
        sortable: true,
      },
      {
        key: "onset_qualifier_label",
        heading: "Onset",
        sortable: true,
      },
    );
  }

  //include original subject and call it Source for D2P
  if (props.category.id.includes("DiseaseToPhenotypicFeature")) {
    extraCols.push({
      key: "original_subject",
      heading: "Source",
      sortable: true,
    });
  }

  /** put divider to separate base cols from extra cols */
  if (extraCols[0]) extraCols.unshift({ slot: "divider" });

  return [...baseCols, ...extraCols];
});

/** get table association data */

// 1) query direct‐only once:
const {
  data: directData,
  query: fetchDirect,
  isLoading: loadingDirect,
  isError: errorDirect,
} = useQuery(
  () =>
    getAssociations(
      props.node.id,
      props.category.id,
      start.value,
      perPage.value,
      true,
      "true",
      props.search,
      sort.value,
    ),
  { items: [], total: 0, limit: 0, offset: 0 },
);

// 2) query all‐(inferred) once:
const {
  data: allData,
  query: fetchAll,
  isLoading: loadingAll,
  isError: errorAll,
} = useQuery(
  () =>
    getAssociations(
      props.node.id,
      props.category.id,
      start.value,
      perPage.value,
      true,
      "false",
      props.search,
      sort.value,
    ),
  { items: [], total: 0, limit: 0, offset: 0 },
);

// pick the right one for rendering:
const associations = computed(() =>
  props.direct.id === "true" ? directData.value : allData.value,
);
const isLoading = computed(() =>
  props.direct.id === "true" ? loadingDirect.value : loadingAll.value,
);
const isError = computed(() =>
  props.direct.id === "true" ? errorDirect.value : errorAll.value,
);

/** download table data */
async function download() {
  /** warn user */
  snackbar(
    `Downloading data for ${
      associations.value.total > maxDownload ? "first " : ""
    }${Math.min(
      associations.value.total,
      maxDownload,
    )} table rows. This may take a minute.`,
  );

  /** download as many rows as possible */
  await downloadAssociations(
    props.node.id,
    props.category.id,
    true,
    props.direct.id,
    props.search,
    sort.value,
  );
}

/** get phenotype frequency percentage 0-1 */
const frequencyPercentage = (row: DirectionalAssociation) => {
  /** frequency from % out of 100 */
  if (row.has_percentage != undefined) return row.has_percentage / 100;

  /** frequency from ratio */
  if (row.has_count != undefined && row.has_total != undefined) {
    return row.has_count / row.has_total;
  }
  /** enumerated frequencies */
  if (row.frequency_qualifier != undefined)
    switch (row.frequency_qualifier) {
      case "HP:0040280":
        return 1;
      case "HP:0040281":
        return 0.8;
      case "HP:0040282":
        return 0.3;
      case "HP:0040283":
        return 0.05;
      case "HP:0040284":
        return 0.01;
      default:
        return 0;
    }
};

/** get frequency tooltip */

const frequencyTooltip = (row: DirectionalAssociation) => {
  // display fraction if possible
  if (row.has_count != undefined && row.has_total != undefined) {
    return `${row.has_count} of ${row.has_total} cases`;
  }

  // if percentage is present but fraction isn't, that's what was originally in the data
  if (row.has_percentage != undefined && row.has_total != undefined) {
    return `${row.has_percentage.toFixed(0)}%`;
  }
  // if no percentage or fraction, display the qualifier label
  if (row.frequency_qualifier) return `${row.frequency_qualifier_label}`;

  // finally, there is no frequency info at all
  return "No info";
};

watch(
  () => props.search,
  async (newSearch, oldSearch) => {
    if (props.direct.id === "true") {
      await fetchDirect();
    } else {
      await fetchAll();
    }
  },
  { immediate: true },
);

watch([perPage, sort, start], async () => {
  if (props.direct.id === "true") {
    await fetchDirect();
  } else {
    await fetchAll();
  }
});

const inferredLabel = computed(() => {
  const rows = allData.value?.items ?? [];
  console.log("rows", rows);
  const useField = fieldFor(props.category.id);
  const hit = rows.find(
    (r) =>
      typeof (r as any)[useField] === "string" &&
      (r as any)[useField].trim().length > 0,
  );
  return (hit as any)?.[useField] ?? "";
});

// watchEffect(() => {
//   console.log(
//     "CAT",
//     props.category.id,
//     "items",
//     allData.value?.items?.length ?? 0,
//     "inferred",
//     inferredDiseaseSubject.value,
//   );
// });

// emit when the inferred subject appears
// let emittedOnce = false;
// watch(
//   () => inferredDiseaseSubject.value,
//   (label) => {
//     // remove the flag if you want re-emits
//     if (!label || emittedOnce) return;
//     emit("update:diseaseSubjectLabel", label);
//     emittedOnce = true;
//   },
//   { immediate: true },
// );

// // reset the "once" flag when node/category changes
// watch([() => props.node.id, () => props.category.id], () => {
//   emittedOnce = false;
// });

watch(
  () => inferredLabel.value,
  (label) => {
    if (label) {
      emit("inferred-label", { categoryId: String(props.category.id), label });
    }
  },
  { immediate: true },
);

onMounted(async () => {
  // Trigger both queries
  await Promise.all([fetchDirect(), fetchAll()]);
});

// Whenever either total changes, emit new totals
watch(
  [() => directData.value?.total, () => allData.value?.total],
  ([newDirectTotal, newAllTotal]) => {
    emit("totals", {
      direct: newDirectTotal ?? 0,
      all: newAllTotal ?? 0,
    });
  },
  { immediate: true },
);
</script>

<style lang="scss" scoped>
.arrow {
  color: $gray;
}

.details {
  width: 100%;
  min-height: unset !important;
}

.empty {
  color: $gray;
}

.loading {
  display: flex;
  flex-direction: column-reverse;
  align-items: center;
  justify-content: center;
  width: 100%;
  animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.7;
  }
}

.badgeColumn {
  display: flex;
  flex-direction: column;
  gap: 0.2em;
}

.text-sm {
  color: $dark-gray;
  font-size: 0.9em;
}
.negated-text {
  color: $error;
  font-weight: bold;
}
</style>
