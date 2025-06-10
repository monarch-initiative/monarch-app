<!--
  node page associations section, table mode. all associations.
-->

<template>
  <div class="association-tabs">
    <button
      :class="{ active: selectedTab === 'all' }"
      @click="selectedTab = 'all'"
    >
      All
    </button>
    <button
      :class="{ active: selectedTab === 'direct' }"
      @click="selectedTab = 'direct'"
    >
      Direct
    </button>
  </div>
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
            name:
              row?.highlighting?.subject_closure_label?.[0] ||
              row.subject_label,
            category: row.subject_category,
            info: row.subject_taxon_label,
          }"
          :breadcrumbs="getBreadcrumbs(node, row, 'subject')"
          :get-highlighted-text="getHighlightedText"
        />

        <AppNodeText
          v-if="row?.highlighting?.subject_closure_label?.[0]"
          :text="`Ancestor: ${row.highlighting.subject_closure_label[0]}`"
          class="text-sm"
          :get-highlighted-text="getHighlightedText"
        />
      </div>
    </template>

    <!-- predicate -->
    <template #predicate="{ row }">
      <AppPredicateBadge
        :association="row"
        :get-highlighted-text="getHighlightedText"
      />
    </template>

    <!-- maxorelation -->
    <template #maxorelation="{ row }">
      {{ row.original_predicate }}
    </template>

    <!-- object-->
    <template #object="{ row }">
      <div class="badgeColumn">
        <AppNodeBadge
          :node="{
            id: row.object,
            name:
              row?.highlighting?.object_closure_label?.[0] || row.object_label,
            category: row.object_category,
            info: row.object_taxon_label,
          }"
          :breadcrumbs="getBreadcrumbs(node, row, 'object')"
          :get-highlighted-text="getHighlightedText"
        />
        <AppNodeText
          v-if="row?.highlighting?.object_closure_label?.[0]"
          :text="`Ancestor: ${row.highlighting.object_closure_label[0]}`"
          class="text-sm"
          :get-highlighted-text="getHighlightedText"
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
import { getBreadcrumbs } from "@/pages/node/AssociationsSummary.vue";
import SectionAssociationDetails from "@/pages/node/SectionAssociationDetails.vue";

type Props = {
  /** current node */
  node: Node;
  /** selected association category */
  category: Option;
  /** include orthologs */
  includeOrthologs: boolean;
  direct: Option;
  /** search string */
  search: string;
};

const props = defineProps<Props>();
const selectedTab = ref<"all" | "direct">("all");
const showModal = ref(false);
const selectedAssociation = ref<DirectionalAssociation | null>(null);
const start = ref(0);
const sort = ref<Sort>();
const perPage = ref(5);

const directParam = computed(() => {
  return selectedTab.value === "direct"
    ? { id: true, label: "Direct" }
    : { id: undefined, label: "All" };
});

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

const getHighlightedText = (
  text: string,
  transformFn?: (text: string) => string,
): string => {
  if (!text) return "";
  const transformed = transformFn ? transformFn(text) : text;
  if (!props.search) return transformed;
  const regex = new RegExp(props.search, "gi");
  return transformed.replace(
    regex,
    (match) => `<span style="background: #FFFF00;"><em>${match}</em></span>`,
  );
};

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
  const baseCols: Cols<Datum> = [
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
  /** publication specific columns */
  // if (props.category.label === "biolink:Publication")
  //   extraCols.push(
  //     {
  //       key: "author",
  //       heading: "Author",
  //     },
  //     {
  //       key: "year",
  //       heading: "Year",
  //       align: "center",
  //     },
  //     {
  //       key: "publisher",
  //       heading: "Publisher",
  //     },
  //   );

  /** filter out extra columns with nothing in them (all rows for that col falsy) */
  // extraCols = extraCols.filter((col) =>
  //   associations.value.items.some((association) =>
  //     col.key ? association[col.key] : true,
  //   ),
  // );

  /** put divider to separate base cols from extra cols */
  if (extraCols[0]) extraCols.unshift({ slot: "divider" });

  return [...baseCols, ...extraCols];
});

/** get table association data */

const {
  query: queryAssociations,
  data: associations,
  isLoading,
  isError,
} = useQuery<
  {
    items: DirectionalAssociation[];
    total: number;
    limit: number;
    offset: number;
  },
  [boolean]
>(
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async function (fresh: boolean) /**
   * whether to perform "fresh" search, without filters/pagination/etc. true when
   * search text changes, false when filters/pagination/etc change.
   */ {
    /** catch case where no association categories available */
    if (!props.node.association_counts.length)
      throw Error("No association info available");
    /** get association data */
    if (fresh) {
      start.value = 0;
    }

    const params: any = {
      nodeId: props.node.id,
      categoryId: props.category.id,
      start: start.value,
      limit: perPage.value,
      includeOrthologs: props.includeOrthologs,
      search: props.search,
      sort: sort.value,
    };

    //  Only add direct param if defined
    if (directParam.value.id !== undefined) {
      params.direct = directParam.value.id;
    }

    const response = await getAssociations(
      params.nodeId,
      params.categoryId,
      params.start,
      params.limit,
      params.includeOrthologs,
      params.direct,
      params.search,
      params.sort,
    );
    return response;
  },

  /** default value */
  { items: [], total: 0, limit: 0, offset: 0 },
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
    props.includeOrthologs,
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

/** get associations when category or table state changes */
watch(
  () => props.category,
  async () => await queryAssociations(true),
);
watch(
  () => props.includeOrthologs,
  async () => await queryAssociations(true),
);
watch(
  () => directParam.value,
  async () => await queryAssociations(true),
);

watch(
  () => props.search,
  async () => {
    await queryAssociations(true);
  },
  { immediate: true },
);

watch([perPage, sort, start], async () => await queryAssociations(false));

/** get associations on load */
onMounted(() => queryAssociations(true));
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
</style>
