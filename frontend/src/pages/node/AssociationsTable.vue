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
    v-model:per-page="perPage"
    v-model:start="start"
    v-model:search="search"
    :cols="cols"
    :rows="associations.items"
    :total="associations.total"
    :sort="sort"
    @download="download"
    @sort="(value: Sort) => (sort = value)"
  >
    <!-- "subject" (current node) -->
    <template #subject="{ row }">
      <AppNodeBadge
        :node="{
          id: row.subject,
          name: row.subject_label,
          category: row.subject_category,
        }"
        :link="node.id === row.object"
      />
    </template>

    <!-- "predicate" (association/relation) -->
    <template #association="{ row }">
      <AppPredicateBadge :association="row as DirectionalAssociation" />
    </template>

    <!-- "object" (what current node has an association with) -->
    <template #object="{ row }">
      <AppNodeBadge
        :node="{
          id: row.object,
          name: row.object_label,
          category: row.object_category,
        }"
        :link="node.id === row.subject"
      />
    </template>

    <!-- button to show evidence -->
    <template #evidence="{ cell, row }">
      <AppButton
        v-tooltip="
          row.id === association?.id
            ? 'Viewing supporting evidence. Click again to hide.'
            : 'View supporting evidence for this association'
        "
        class="evidence"
        :text="String(cell || 0)"
        :aria-pressed="row.id === association?.id"
        :icon="row.id === association?.id ? 'check' : 'flask'"
        :color="row.id === association?.id ? 'primary' : 'secondary'"
        @click="
          emit(
            'select',
            (row.id === association?.id
              ? undefined
              : row) as DirectionalAssociation,
          )
        "
      />
    </template>

    <!-- extra columns -->

    <!-- taxon specific -->
    <template #taxon="{ cell }">
      <span class="truncate">
        {{ cell?.name }}
      </span>
    </template>

    <!-- phenotype specific -->
    <template #frequency="{ cell }">
      <AppLink v-if="cell" class="truncate" :to="cell?.link" :no-icon="true">
        {{ cell?.name }}
      </AppLink>
    </template>

    <template #onset="{ cell }">
      <AppLink v-if="cell" class="truncate" :to="cell?.link" :no-icon="true">
        {{ cell?.name }}
      </AppLink>
    </template>

    <!-- publication specific -->
    <!-- no template needed because info just plain text -->
  </AppTable>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { getAssociations } from "@/api/associations";
import { getCategoryLabel } from "@/api/categories";
import type { DirectionalAssociation, Node } from "@/api/model";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppPredicateBadge from "@/components/AppPredicateBadge.vue";
import type { Option } from "@/components/AppSelectSingle.vue";
import AppTable from "@/components/AppTable.vue";
import type { Cols, Sort } from "@/components/AppTable.vue";
import { snackbar } from "@/components/TheSnackbar.vue";
import { useQuery } from "@/util/composables";
import { downloadJson } from "@/util/download";

interface Props {
  /** current node */
  node: Node;
  /** selected association category */
  category: Option;
  /** selected association */
  association?: DirectionalAssociation;
}

const props = defineProps<Props>();

interface Emits {
  /** change selected association */
  (event: "select", value?: DirectionalAssociation): void;
}

const emit = defineEmits<Emits>();

/** table state */
const sort = ref<Sort>();
const perPage = ref(5);
const start = ref(0);
const search = ref("");

/** table columns */
const cols = computed((): Cols => {
  /** standard columns, always present */
  const baseCols: Cols = [
    {
      id: "subject",
      key: "",
      heading: getCategoryLabel(
        associations.value.items[0]?.subject_category || "Subject",
      ),
      width: "max-content",
    },
    {
      id: "association",
      key: "",
      heading: "Association",
      width: "max-content",
    },
    {
      id: "object",
      key: "",
      heading: getCategoryLabel(
        associations.value.items[0]?.object_category || "Object",
      ),
      width: "max-content",
    },
    {
      id: "evidence",
      key: "evidence_count",
      heading: "Evidence",
      width: "min-content",
      align: "center",
    },
  ];

  /** extra, supplemental columns for certain association types */
  let extraCols: Cols = [];

  /** taxon column. exists for many categories, so just add if any row has taxon. */
  if (associations.value.items.some(() => ""))
    extraCols.push({
      id: "taxon",
      key: "taxon",
      heading: "Taxon",
      width: "max-content",
    });

  /** phenotype specific columns */
  if (
    props.category.label === "biolink:DiseaseToPhenotypicFeatureAssociation"
  ) {
    extraCols.push(
      {
        id: "frequency",
        key: "frequency_qualifier_label",
        heading: "Frequency",
        sortable: true,
      },
      {
        id: "onset",
        key: "onset_qualifier_label",
        heading: "Onset",
        sortable: true,
      },
    );
  }

  /** publication specific columns */
  if (props.category.label === "biolink:Publication")
    extraCols.push(
      {
        id: "author",
        key: "author",
        heading: "Author",
        width: "max-content",
      },
      {
        id: "year",
        key: "year",
        heading: "Year",
        align: "center",
        width: "max-content",
      },
      {
        id: "publisher",
        key: "publisher",
        heading: "Publisher",
        width: "max-content",
      },
    );

  /**
   * filter out extra columns with nothing in them (all rows for that col
   * falsey)
   */
  // extraCols = extraCols.filter((col) =>
  //   associations.value.items.some(
  //     (association) => association[(col.key || "") as keyof typeof association]
  //   )
  // );

  /** put divider to separate base cols from extra cols */
  if (extraCols[0]) extraCols.unshift({ id: "divider" });

  return [...baseCols, ...extraCols];
});

/** get table association data */
const {
  query: queryAssociations,
  data: associations,
  isLoading,
  isError,
} = useQuery(
  async function (
    /**
     * whether to perform "fresh" search, without filters/pagination/etc. true
     * when search text changes, false when filters/pagination/etc change.
     */
    fresh: boolean,
  ) {
    /** catch case where no association categories available */
    if (!props.node.association_counts.length)
      throw new Error("No association info available");

    /** get association data */
    const response = await getAssociations(
      props.node.id,
      props.category.id,
      start.value,
      perPage.value,
      search.value,
    );

    return response;
  },

  /** default value */
  { items: [], total: 0, limit: 0, offset: 0 },
);

/** download table data */
async function download() {
  /** max rows to try to query */
  const max = 100000;

  /** warn user */
  snackbar(
    `Downloading data for ${Math.min(
      associations.value.total,
      max,
    )} table entries.` +
      (associations.value.total >= 100 ? " This may take a minute." : ""),
  );

  /** attempt to request all rows */
  const response = await getAssociations(
    props.node.id,
    props.category.id,
    0,
    max,
  );
  downloadJson(response);
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

.evidence {
  width: 100%;
  min-height: unset !important;
}
</style>