<!--
  node page associations section, table mode. all associations.
-->

<template>
  <!-- status -->
  <AppStatus v-if="isLoading" code="loading"
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
    v-model:search="search"
    :cols="cols"
    :rows="associations.items"
    :total="associations.total"
    @download="download"
  >
    <!-- subject -->
    <template #subject="{ row }">
      <AppNodeBadge
        :node="{
          id: row.subject,
          name: row.subject_label,
          category: row.subject_category,
          info: row.subject_taxon_label,
        }"
        :breadcrumbs="getBreadcrumbs(node, row, 'subject')"
      />
    </template>

    <!-- predicate -->
    <template #predicate="{ row }">
      <AppPredicateBadge :association="row" />
    </template>

    <!-- object-->
    <template #object="{ row }">
      <AppNodeBadge
        :node="{
          id: row.object,
          name: row.object_label,
          category: row.object_category,
          info: row.object_taxon_label,
        }"
        :breadcrumbs="getBreadcrumbs(node, row, 'object')"
      />
    </template>

    <template #frequency="{ row }">
      <AppPercentage
        v-if="frequencyPercentage(row) !== undefined"
        type="bar"
        :percent="frequencyPercentage(row) || 0"
        :tooltip="frequencyTooltip(row)"
      />
      <span v-else class="empty">No info</span>
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

    <!-- phenotype specific -->
    <!-- no template needed because info just plain text -->

    <!-- publication specific -->
    <!-- no template needed because info just plain text -->
  </AppTable>
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
import AppPercentage from "@/components/AppPercentage.vue";
import AppPredicateBadge from "@/components/AppPredicateBadge.vue";
import type { Option } from "@/components/AppSelectSingle.vue";
import AppTable from "@/components/AppTable.vue";
import type { Cols, Sort } from "@/components/AppTable.vue";
import { snackbar } from "@/components/TheSnackbar.vue";
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
};

const props = defineProps<Props>();

const showModal = ref(false);
const selectedAssociation = ref<DirectionalAssociation | null>(null);

function openModal(association: DirectionalAssociation) {
  selectedAssociation.value = association;
  showModal.value = true;
}

watch(showModal, (newValue) => {
  if (!newValue) {
    selectedAssociation.value = null;
  }
});

// type Emits = {
//   /** change selected association */
//   select: [value?: DirectionalAssociation];
// };
//
// const emit = defineEmits<Emits>();
//
// emit("select", (value) => {
//   if (value) {
//     console.log("emitting association detail event");
//     console.log(value);
//     association.value = value;
//     showModal.value = true;
//   }
// });

/** table state */
const sort = ref<Sort>();
const perPage = ref(5);
const start = ref(0);
const search = ref("");

type Datum = keyof DirectionalAssociation;

/** table columns */
const cols = computed((): Cols<Datum> => {
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
  if (
    associations.value.items.some(
      (item) => item.subject_taxon_label || item.object_taxon_label,
    )
  )
    extraCols.push({
      slot: "taxon",
      heading: "Taxon",
    });

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
} = useQuery(
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
    const response = await getAssociations(
      props.node.id,
      props.category.id,
      start.value,
      perPage.value,
      props.includeOrthologs,
      props.direct.id,
      search.value,
      sort.value,
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
    search.value,
    sort.value,
  );
}

/** get phenotype frequency percentage 0-1 */
const frequencyPercentage = (row: DirectionalAssociation) => {
  /** frequency from % out of 100 */
  if (row.has_percentage !== undefined) return row.has_percentage / 100;

  /** frequency from ratio */
  if (row.has_count !== undefined && row.has_total !== undefined) {
    return row.has_count / row.has_total;
  }
  /** enumerated frequencies */
  if (row.frequency_qualifier !== undefined)
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
  if (row.has_count !== undefined && row.has_total !== undefined) {
    return `${row.has_count} of ${row.has_total} cases`;
  }

  // if percentage is present but fraction isn't, that's what was originally in the data
  if (row.has_percentage !== undefined && row.has_total !== undefined) {
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
  () => props.direct,
  async () => await queryAssociations(true),
);
watch(
  [perPage, start, search, sort],
  async () => await queryAssociations(false),
);

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
</style>
