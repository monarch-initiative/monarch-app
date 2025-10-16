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
    <template #primary_knowledge_source="{ row }">
      <span v-if="sourceNames(row.primary_knowledge_source).length">
        {{ sourceNames(row.primary_knowledge_source).join(", ") }}
      </span>
      <span v-else class="empty">No info</span>
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
import { computed, onMounted, ref, watch } from "vue";
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
import { RESOURCE_NAME_MAP } from "@/config/resourceNames";
import {
  buildAssociationCols,
  type Datum,
} from "@/pages/node/associationColumns";
import { getBreadcrumbs } from "@/pages/node/AssociationsSummary.vue";
import SectionAssociationDetails from "@/pages/node/SectionAssociationDetails.vue";
import { fieldFor } from "@/util/typeConfig";

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

const props = withDefaults(defineProps<Props>(), {
  search: "",
});

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

const openModal = (association: DirectionalAssociation) => {
  selectedAssociation.value = association;
  showModal.value = true;
};

watch(showModal, (newValue) => {
  if (!newValue) {
    selectedAssociation.value = null;
  }
});

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

/** table columns */
const cols = computed((): Cols<Datum> => {
  if (props.category.id.includes("GeneToGeneHomology")) {
    return orthologColoumns.value;
  }

  return buildAssociationCols({
    categoryId: props.category.id,
    nodeCategory: props.node.category ?? "",
    isDirect: props.direct.id === "true",
    items: associations.value.items as DirectionalAssociation[],
    getCategoryLabel,
  });
});

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

// which side is relevant for this category?
const side = computed<"subject" | "object">(() => fieldFor(props.category.id));
const idKey = computed<"subject" | "object">(() => side.value);
const closureKey = computed<"subject_closure" | "object_closure">(
  () => `${side.value}_closure` as const,
);

const labelKey = computed<"subject_label" | "object_label">(
  () => `${side.value}_label` as const,
);

// row comes from a subclass of the current page node?
const isSubclassRow = (row: any, currentNodeId: string): boolean => {
  const id = row?.[idKey.value] as string | undefined;
  const closure: string[] = Array.isArray(row?.[closureKey.value])
    ? row[closureKey.value]
    : [];
  return !!id && id !== currentNodeId && closure.includes(currentNodeId);
};

// pick the first subclass row in the inferred/all set and return its label
const inferredSubclassLabel = computed<string>(() => {
  const rows = allData.value?.items ?? [];
  const pageId = props.node.id;

  if (props.category.id === "biolink:GeneToPhenotypicFeatureAssociation") {
    const hit = rows.find(
      (r: any) =>
        typeof r?.disease_context_qualifier_label === "string" &&
        r.disease_context_qualifier_label.trim().length > 0,
    );
    if (hit) return hit.disease_context_qualifier_label as string;
  }

  const hit = rows.find((row) => isSubclassRow(row, pageId));
  const label = hit?.[labelKey.value];
  return typeof label === "string" ? label : "";
});

const toLabel = (v: unknown) =>
  (String(v).split(":").pop() || "").toUpperCase();

const resourceFullName = (label?: string) =>
  RESOURCE_NAME_MAP[(label ?? "").toUpperCase()] ?? label ?? "";

const sourceNames = (val?: string | string[]) => {
  const list = Array.isArray(val) ? val : val ? [val] : [];
  const seen = new Set<string>();
  return list
    .map(toLabel) // e.g., "infores:uniprot" -> "UNIPROT"
    .map(resourceFullName) // -> "Universal Protein Resource"
    .filter((n) => {
      if (!n || seen.has(n)) return false;
      seen.add(n);
      return true;
    });
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

onMounted(async () => {
  // Trigger both queries
  await Promise.all([fetchDirect(), fetchAll()]);
});

// Whenever either total changes, emit new totals
watch(
  [
    () => inferredSubclassLabel.value,
    () => directData.value?.total ?? 0,
    () => allData.value?.total ?? 0,
  ],
  ([label, direct, all], [prevLabel, prevDirect, prevAll]) => {
    // emit inferred label only when present and changed
    if (label && label !== prevLabel) {
      emit("inferred-label", { categoryId: String(props.category.id), label });
    }
    // emit totals only when they change
    if (direct !== prevDirect || all !== prevAll) {
      emit("totals", { direct, all });
    }
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
