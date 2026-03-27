<!--
  Entity Grid Playground - Test the generic entity grid API with configurable parameters
-->

<template>
  <AppSection width="full">
    <AppHeading>Entity Grid Playground</AppHeading>
    <p style="margin-bottom: 1rem; color: #666">
      Test the generic entity grid API. Search for an entity and select
      association categories to load a grid dynamically.
    </p>

    <div class="examples-section">
      <span class="examples-label">Quick examples:</span>
      <AppButton
        v-for="example in examples"
        :key="example.id"
        :text="example.label"
        design="small"
        color="secondary"
        @click="loadExample(example)"
      />
    </div>

    <div class="playground-controls">
      <div class="control-group entity-search">
        <label for="entity-search">Context Entity:</label>
        <AppSelectAutocomplete
          id="entity-search"
          v-model="searchText"
          name="Entity Search"
          placeholder="Search for gene, disease, phenotype..."
          :options="runGetAutocomplete"
          @change="onEntitySelect"
        />
        <span v-if="fetchingEntityData" class="fetching-entity">
          Loading associations...
        </span>
        <span v-else-if="selectedEntityId" class="selected-entity">
          Selected: <strong>{{ selectedEntityId }}</strong>
        </span>
      </div>

      <div class="control-group">
        <label for="column-categories">Column Association(s):</label>
        <AppSelectMulti
          id="column-categories"
          v-model="playgroundColumnCategories"
          name="Column Categories"
          :options="columnCategoryOptions"
        />
      </div>

      <div class="control-group">
        <label for="row-categories">Row Association(s):</label>
        <AppSelectMulti
          id="row-categories"
          v-model="playgroundRowCategories"
          name="Row Categories"
          :options="rowCategoryOptions"
        />
      </div>

      <div class="control-group">
        <label for="group-by-category">Category Grid Lines:</label>
        <label class="toggle-switch" for="group-by-category">
          <input
            id="group-by-category"
            v-model="playgroundGroupByCategory"
            type="checkbox"
          />
          <span class="toggle-slider"></span>
          <span class="toggle-label">{{
            playgroundGroupByCategory ? "On" : "Off"
          }}</span>
        </label>
      </div>

      <div class="control-group">
        <label for="column-display-mode">Column Labels:</label>
        <label class="toggle-switch" for="column-display-mode">
          <input
            id="column-display-mode"
            type="checkbox"
            :checked="columnDisplayMode === 'labeled'"
            @change="
              columnDisplayMode = ($event.target as HTMLInputElement).checked
                ? 'labeled'
                : 'numeric'
            "
          />
          <span class="toggle-slider"></span>
          <span class="toggle-label">{{
            columnDisplayMode === "labeled" ? "On" : "Off"
          }}</span>
        </label>
      </div>

      <AppButton
        text="Load Grid"
        icon="download"
        :disabled="playgroundLoading || !selectedEntityId"
        @click="loadPlaygroundGrid"
      />

      <AppStatus v-if="playgroundLoading" code="loading"
        >Loading grid...</AppStatus
      >
      <AppStatus v-if="playgroundError" code="error">{{
        playgroundError
      }}</AppStatus>
    </div>

    <div v-if="playgroundMatrix" class="playground-info">
      <p>
        <strong>{{
          playgroundMatrix.contextName || playgroundMatrix.contextId
        }}</strong
        >: {{ playgroundMatrix.totalColumns }} columns ×
        {{ playgroundMatrix.totalRows }} rows
      </p>
    </div>

    <EntityGrid
      v-if="playgroundMatrix"
      :matrix="playgroundMatrix"
      :config="playgroundConfig"
      @cell-click="handlePlaygroundCellClick"
    />
    <EntityGridModal
      v-model="showPlaygroundModal"
      :column-id="playgroundSelectedColumn?.id || ''"
      :column-label="playgroundSelectedColumn?.label"
      :row-id="playgroundSelectedRow?.id || ''"
      :row-label="playgroundSelectedRow?.label"
      :cell-data="playgroundSelectedCellData"
      :config="playgroundConfig"
    />
  </AppSection>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { getCategoryIcon } from "@/api/categories";
import {
  getEntityGrid,
  getTraversableAssociations,
  type TraversableAssociation,
} from "@/api/entity-grid";
import type {
  CellData,
  ColumnEntity,
  EntityGridConfig,
  EntityGridMatrix,
  RowEntity,
} from "@/api/entity-grid/types";
import { getNode } from "@/api/node";
import { getAutocomplete } from "@/api/search";
import AppButton from "@/components/AppButton.vue";
import type {
  Options as AutocompleteOptions,
  Option,
} from "@/components/AppSelectAutocomplete.vue";
import AppSelectAutocomplete from "@/components/AppSelectAutocomplete.vue";
import AppSelectMulti from "@/components/AppSelectMulti.vue";
import AppStatus from "@/components/AppStatus.vue";
import EntityGrid from "@/components/EntityGrid/EntityGrid.vue";
import EntityGridModal from "@/components/EntityGrid/EntityGridModal.vue";

// =============================================================================
// Quick Examples
// =============================================================================

interface Example {
  id: string;
  label: string;
  entityId: string;
  entityName: string;
  columnCategories: string[];
  rowCategories: string[];
  groupByCategory: boolean;
}

const examples: Example[] = [
  {
    id: "gene-disease",
    label: "HTT Gene (Huntington)",
    entityId: "HGNC:4851",
    entityName: "HTT",
    columnCategories: ["biolink:CausalGeneToDiseaseAssociation"],
    rowCategories: ["biolink:DiseaseToPhenotypicFeatureAssociation"],
    groupByCategory: false,
  },
  {
    id: "gene-causal-correlated",
    label: "BRCA1 (Causal + Correlated)",
    entityId: "HGNC:1100",
    entityName: "BRCA1",
    columnCategories: [
      "biolink:CausalGeneToDiseaseAssociation",
      "biolink:CorrelatedGeneToDiseaseAssociation",
    ],
    rowCategories: ["biolink:DiseaseToPhenotypicFeatureAssociation"],
    groupByCategory: true,
  },
  {
    id: "disease-cases",
    label: "Marfan Syndrome (Cases)",
    entityId: "MONDO:0007947",
    entityName: "Marfan syndrome",
    columnCategories: ["biolink:CaseToDiseaseAssociation"],
    rowCategories: ["biolink:CaseToPhenotypicFeatureAssociation"],
    groupByCategory: false,
  },
];

/** Load an example configuration and trigger grid load */
async function loadExample(example: Example) {
  // Populate the form
  searchText.value = example.entityName;
  selectedEntityId.value = example.entityId;
  playgroundGroupByCategory.value = example.groupByCategory;

  // Fetch entity associations to populate options
  await fetchEntityAssociations(example.entityId);

  // Set the selected categories (after options are populated)
  playgroundColumnCategories.value = example.columnCategories.map((id) => ({
    id,
  }));
  playgroundRowCategories.value = example.rowCategories.map((id) => ({ id }));

  // Load the grid
  await loadPlaygroundGrid();
}

// =============================================================================
// Entity Search / Autocomplete
// =============================================================================

/** Current search text in the autocomplete */
const searchText = ref("");
/** Selected entity ID */
const selectedEntityId = ref("");
/** Selected entity's biolink category */
const selectedEntityCategory = ref("");
/** Traversable associations for the selected entity type */
const traversableAssociations = ref<TraversableAssociation[]>([]);

/** Get autocomplete results from the search API */
async function runGetAutocomplete(
  search: string,
): Promise<AutocompleteOptions> {
  if (!search.trim()) return [];

  const response = await getAutocomplete(search);
  return response.items.map((item) => ({
    id: item.id,
    label: item.name || item.id,
    info: item.in_taxon_label || item.id,
    icon: getCategoryIcon(item.category),
  }));
}

/** Handle entity selection from autocomplete */
async function onEntitySelect(value: string | Option) {
  const entityId = typeof value === "string" ? value : value.id;
  if (!entityId) return;

  selectedEntityId.value = entityId;
  if (typeof value !== "string") {
    searchText.value = value.label;
  }

  // Fetch node data to get association counts
  await fetchEntityAssociations(entityId);
}

/** Fetch entity data and populate association category options dynamically */
async function fetchEntityAssociations(entityId: string) {
  fetchingEntityData.value = true;
  try {
    // Fetch the node to get its category and association counts
    const node = await getNode(entityId);

    // Store entity category
    const category = Array.isArray(node.category)
      ? node.category[0]
      : node.category;
    selectedEntityCategory.value = category || "";

    // Fetch traversable associations for this entity type
    if (category) {
      try {
        traversableAssociations.value =
          await getTraversableAssociations(category);
      } catch (e) {
        console.warn("Failed to fetch traversable associations:", e);
        traversableAssociations.value = [];
      }
    }

    // Build column options from traversable associations, with counts from node data
    const countsByCategory = new Map<string, number>();
    for (const assocCount of node.association_counts || []) {
      const cat = assocCount.category || assocCount.label;
      if (cat) {
        countsByCategory.set(cat, assocCount.count || 0);
      }
    }

    // Filter traversable associations to those with counts > 0 (or all if no counts)
    const newColumnOptions: Array<{
      id: string;
      label: string;
      count?: number;
      targetCategory?: string;
    }> = [];

    for (const assoc of traversableAssociations.value) {
      // Skip associations that go directly to phenotypes - those are row options, not column options
      if (assoc.targetCategory === "biolink:PhenotypicFeature") {
        continue;
      }
      const count = countsByCategory.get(assoc.category) || 0;
      // Include associations that have counts, or all if no counts available
      if (count > 0 || countsByCategory.size === 0) {
        newColumnOptions.push({
          id: assoc.category,
          label: count > 0 ? `${assoc.label} (${count})` : assoc.label,
          count,
          targetCategory: assoc.targetCategory,
        });
      }
    }

    // Sort by count descending
    newColumnOptions.sort((a, b) => (b.count || 0) - (a.count || 0));

    if (newColumnOptions.length > 0) {
      columnCategoryOptions.value = newColumnOptions;
      // Auto-select first option if nothing selected
      if (playgroundColumnCategories.value.length === 0) {
        playgroundColumnCategories.value = [{ id: newColumnOptions[0].id }];
      }
    } else {
      // No traversable associations found - clear options
      columnCategoryOptions.value = [];
    }

    // Update row options based on initial column selection
    updateRowOptions();
  } catch (e) {
    console.warn("Failed to fetch entity associations:", e);
    columnCategoryOptions.value = [];
    traversableAssociations.value = [];
  } finally {
    fetchingEntityData.value = false;
  }
}

/** Update row options based on selected column associations' target categories */
function updateRowOptions() {
  // Get target categories from selected column associations
  const selectedColumnIds = playgroundColumnCategories.value.map((c) => c.id);
  const targetCategories = new Set<string>();

  for (const colId of selectedColumnIds) {
    const assoc = traversableAssociations.value.find(
      (a) => a.category === colId,
    );
    if (assoc?.targetCategory) {
      targetCategories.add(assoc.targetCategory);
    }
  }

  // Find row associations that go FROM the target categories TO phenotypes
  const newRowOptions: Array<{ id: string; label: string }> = [];

  // Row associations map: target category -> phenotype associations
  const rowAssociationMap: Record<
    string,
    Array<{ category: string; label: string }>
  > = {
    "biolink:Disease": [
      {
        category: "biolink:DiseaseToPhenotypicFeatureAssociation",
        label: "Disease-Phenotype",
      },
    ],
    "biolink:Gene": [
      {
        category: "biolink:GeneToPhenotypicFeatureAssociation",
        label: "Gene-Phenotype",
      },
    ],
    "biolink:Case": [
      {
        category: "biolink:CaseToPhenotypicFeatureAssociation",
        label: "Case-Phenotype",
      },
    ],
    "biolink:Genotype": [
      {
        category: "biolink:GenotypeToPhenotypicFeatureAssociation",
        label: "Genotype-Phenotype",
      },
    ],
    "biolink:SequenceVariant": [
      {
        category: "biolink:VariantToPhenotypicFeatureAssociation",
        label: "Variant-Phenotype",
      },
    ],
  };

  // Collect row options from all target categories
  const seenRowCategories = new Set<string>();
  for (const targetCat of targetCategories) {
    const rowAssocs = rowAssociationMap[targetCat] || [];
    for (const rowAssoc of rowAssocs) {
      if (!seenRowCategories.has(rowAssoc.category)) {
        seenRowCategories.add(rowAssoc.category);
        newRowOptions.push({
          id: rowAssoc.category,
          label: rowAssoc.label,
        });
      }
    }
  }

  if (newRowOptions.length > 0) {
    rowCategoryOptions.value = newRowOptions;
    // Auto-select first row option if nothing selected or if current selection is invalid
    const currentIds = playgroundRowCategories.value.map((r) => r.id);
    const validSelection = currentIds.some((id) =>
      newRowOptions.some((opt) => opt.id === id),
    );
    if (playgroundRowCategories.value.length === 0 || !validSelection) {
      playgroundRowCategories.value = [{ id: newRowOptions[0].id }];
    }
  } else {
    // No valid row options - use default phenotype associations
    rowCategoryOptions.value = Object.entries(allRowCategoryOptions).map(
      ([id, label]) => ({ id, label }),
    );
  }
}

// =============================================================================
// Entity Grid Playground
// =============================================================================

/** Playground state */
const playgroundColumnCategories = ref([
  { id: "biolink:CausalGeneToDiseaseAssociation" },
]);
const playgroundRowCategories = ref([
  { id: "biolink:DiseaseToPhenotypicFeatureAssociation" },
]);
const playgroundGroupByCategory = ref(true);
const columnDisplayMode = ref<"numeric" | "labeled">("labeled");
const playgroundLoading = ref(false);
const playgroundError = ref("");
const playgroundMatrix = ref<EntityGridMatrix | null>(null);

/** All possible column category options (with friendly labels) */
const allColumnCategoryOptions: Record<string, string> = {
  "biolink:CausalGeneToDiseaseAssociation": "Causal Gene-Disease",
  "biolink:CorrelatedGeneToDiseaseAssociation": "Correlated Gene-Disease",
  "biolink:CaseToDiseaseAssociation": "Case-Disease",
  "biolink:GeneToGeneHomologyAssociation": "Gene Homology (Orthologs)",
};

/** All possible row category options */
const allRowCategoryOptions: Record<string, string> = {
  "biolink:DiseaseToPhenotypicFeatureAssociation": "Disease-Phenotype",
  "biolink:CaseToPhenotypicFeatureAssociation": "Case-Phenotype",
  "biolink:GeneToPhenotypicFeatureAssociation": "Gene-Phenotype",
};

/** Dynamic options based on selected entity */
const columnCategoryOptions = ref<
  Array<{ id: string; label: string; count?: number }>
>(
  // Initialize with all options (no counts) until entity is selected
  Object.entries(allColumnCategoryOptions).map(([id, label]) => ({
    id,
    label,
  })),
);
const rowCategoryOptions = ref<Array<{ id: string; label: string }>>(
  Object.entries(allRowCategoryOptions).map(([id, label]) => ({ id, label })),
);

/** Loading state for fetching entity data */
const fetchingEntityData = ref(false);

/** Watch column category selection to update row options */
watch(
  playgroundColumnCategories,
  () => {
    // Only update if we have traversable associations loaded
    if (traversableAssociations.value.length > 0) {
      updateRowOptions();
    }
  },
  { deep: true },
);

/** Playground config (computed to react to display mode changes) */
const playgroundConfig = computed<EntityGridConfig>(() => ({
  columnLabel: "Entity",
  columnLabelPlural: "Entities",
  rowLabel: "Phenotype",
  rowLabelPlural: "Phenotypes",
  binLabel: "System",
  cellDisplayMode: "binary",
  showNegated: true,
  columnDisplayMode: columnDisplayMode.value,
  showColumnGroupSeparators: playgroundGroupByCategory.value,
}));

/** Playground modal state */
const showPlaygroundModal = ref(false);
const playgroundSelectedColumn = ref<ColumnEntity | null>(null);
const playgroundSelectedRow = ref<RowEntity | null>(null);
const playgroundSelectedCellData = ref<CellData | null>(null);

/** Load grid from API */
async function loadPlaygroundGrid() {
  if (!selectedEntityId.value) {
    playgroundError.value = "Please select an entity";
    return;
  }

  if (playgroundColumnCategories.value.length === 0) {
    playgroundError.value =
      "Please select at least one column association category";
    return;
  }

  if (playgroundRowCategories.value.length === 0) {
    playgroundError.value =
      "Please select at least one row association category";
    return;
  }

  playgroundLoading.value = true;
  playgroundError.value = "";
  playgroundMatrix.value = null;

  try {
    const matrix = await getEntityGrid(selectedEntityId.value, {
      columnAssociationCategory: playgroundColumnCategories.value.map(
        (c) => c.id,
      ),
      rowAssociationCategory: playgroundRowCategories.value.map((c) => c.id),
      groupColumnsByCategory: playgroundGroupByCategory.value,
    });
    playgroundMatrix.value = matrix;
  } catch (e) {
    playgroundError.value = e instanceof Error ? e.message : String(e);
  } finally {
    playgroundLoading.value = false;
  }
}

/** Handle playground cell click */
function handlePlaygroundCellClick(
  columnId: string,
  rowId: string,
  cellData: CellData | null,
) {
  if (!playgroundMatrix.value) return;
  playgroundSelectedColumn.value =
    playgroundMatrix.value.columns.find((c) => c.id === columnId) || null;
  playgroundSelectedRow.value =
    playgroundMatrix.value.rows.find((r) => r.id === rowId) || null;
  playgroundSelectedCellData.value = cellData;
  showPlaygroundModal.value = true;
}
</script>

<style lang="scss" scoped>
.examples-section {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  gap: 0.5rem;
  border-left: 4px solid #ffc107;
  border-radius: 8px;
  background: #fff8e1;
}

.examples-label {
  margin-right: 0.5rem;
  color: #666;
  font-weight: 500;
  font-size: 0.875rem;
}

.playground-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  margin-bottom: 1rem;
  padding: 1rem;
  gap: 1rem;
  border-radius: 8px;
  background: #f5f5f5;
}

.control-group {
  display: flex;
  flex-direction: column;
  min-width: 200px;
  gap: 0.25rem;

  > label {
    color: #666;
    font-weight: 500;
    font-size: 0.875rem;
  }
}

// Toggle switch styles
.toggle-switch {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;

  input {
    position: absolute;
    width: 0;
    height: 0;
    opacity: 0;
  }

  .toggle-slider {
    display: inline-block;
    position: relative;
    width: 40px;
    height: 22px;
    border-radius: 11px;
    background-color: #ccc;
    transition: background-color 0.2s;

    &::before {
      position: absolute;
      top: 2px;
      left: 2px;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background-color: white;
      content: "";
      transition: transform 0.2s;
    }
  }

  input:checked + .toggle-slider {
    background-color: #2196f3;

    &::before {
      transform: translateX(18px);
    }
  }

  .toggle-label {
    min-width: 24px;
    color: #666;
    font-weight: 500;
    font-size: 0.8rem;
  }
}

.entity-search {
  min-width: 350px;
}

.selected-entity {
  margin-top: 0.25rem;
  color: #2196f3;
  font-size: 0.8rem;
}

.fetching-entity {
  margin-top: 0.25rem;
  color: #ff9800;
  font-style: italic;
  font-size: 0.8rem;
}

.playground-info {
  margin-bottom: 1rem;
  padding: 0.5rem 1rem;
  border-left: 4px solid #2196f3;
  border-radius: 4px;
  background: #e8f4fd;
}
</style>
