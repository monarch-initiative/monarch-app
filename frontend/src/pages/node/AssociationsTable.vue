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

    <!-- button to show details -->
    <template #details="{ cell, row }">
      <AppButton
        v-tooltip="
          row.id === association?.id
            ? `Show evidence (${row.evidence_count}) and other info about this association`
            : 'Deselect this association'
        "
        class="details"
        :text="String(cell || 0)"
        :aria-pressed="row.id === association?.id"
        :icon="row.id === association?.id ? 'check' : 'flask'"
        :color="row.id === association?.id ? 'primary' : 'secondary'"
        @click="emit('select', row.id === association?.id ? undefined : row)"
      />
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
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { getAssociations } from "@/api/associations";
import { getCategoryLabel } from "@/api/categories";
import {
  AssociationDirectionEnum,
  type DirectionalAssociation,
  type Node,
} from "@/api/model";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppPredicateBadge from "@/components/AppPredicateBadge.vue";
import type { Option } from "@/components/AppSelectSingle.vue";
import AppTable from "@/components/AppTable.vue";
import type { Cols, Sort } from "@/components/AppTable.vue";
import { snackbar } from "@/components/TheSnackbar.vue";
import { getBreadcrumbs } from "@/pages/node/AssociationsSummary.vue";
import { useQuery } from "@/util/composables";
import { downloadJson } from "@/util/download";

type Props = {
  /** current node */
  node: Node;
  /** selected association category */
  category: Option;
  /** selected association */
  association?: DirectionalAssociation;
};

const props = defineProps<Props>();

type Emits = {
  /** change selected association */
  select: [value?: DirectionalAssociation];
};

const emit = defineEmits<Emits>();

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
      width: 3,
      sortable: true,
    },
    {
      slot: "predicate",
      key: "predicate",
      heading: "Association",
      width: 2,
      sortable: true,
    },
    {
      slot: "object",
      key: "object_label",
      heading: getCategoryLabel(
        associations.value.items[0]?.object_category || "Object",
      ),
      width: 3,
      sortable: true,
    },
    {
      slot: "details",
      key: "evidence_count",
      heading: "Details",
      width: 1,
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
      width: 2,
    });

  /** phenotype specific columns */
  if (
    props.category.label === "biolink:DiseaseToPhenotypicFeatureAssociation"
  ) {
    extraCols.push(
      {
        key: "frequency_qualifier_label",
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

  /** publication specific columns */
  // if (props.category.label === "biolink:Publication")
  //   extraCols.push(
  //     {
  //       key: "author",
  //       heading: "Author",
  //       width: "max-content",
  //     },
  //     {
  //       key: "year",
  //       heading: "Year",
  //       align: "center",
  //       width: "max-content",
  //     },
  //     {
  //       key: "publisher",
  //       heading: "Publisher",
  //       width: "max-content",
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
  async function (fresh: boolean) /**
   * whether to perform "fresh" search, without filters/pagination/etc. true when
   * search text changes, false when filters/pagination/etc change.
   */ {
    /** catch case where no association categories available */
    if (!props.node.association_counts.length)
      throw Error("No association info available");

    /** get association data */
    const response = await getAssociations(
      props.node.id,
      props.category.id,
      start.value,
      perPage.value,
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
  /** max rows to try to query */
  const max = 100;
  const total = associations.value.total;

  /** warn user */
  snackbar(
    `Downloading data for ${total > max ? "first " : ""}${Math.min(
      total,
      max,
    )} table entries.` + (total >= 100 ? " This may take a minute." : ""),
  );

  /** attempt to request all rows */
  const response = await getAssociations(
    props.node.id,
    props.category.id,
    0,
    max,
  );
  downloadJson(response, "associations");
}

/** get associations when category or table state changes */
watch(
  () => props.category,
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
</style>
