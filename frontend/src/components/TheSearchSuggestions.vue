<template>
  <div class="container">
    <hr />
    <p class="label">Examples of relationships you can explore</p>
    <div class="suggestions">
      <div
        v-for="(search, i) in searchSuggestions"
        :key="i"
        class="suggestion-line"
      >
        <AppNodeBadge
          :node="search.source"
          size="small"
          :icon="true"
          class="clickable"
        />
        <span>to</span>
        <AppNodeBadge
          :node="search.target"
          size="small"
          :icon="true"
          class="clickable"
        />
        <span>relationship in</span>
        <AppNodeBadge :node="search.example" class="clickable" :icon="true" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppNodeBadge from "@/components/AppNodeBadge.vue";

defineEmits<{
  (e: "select", nodeId: string): void;
}>();

const searchSuggestions = [
  {
    source: {
      id: "MONDO:0000001",
      name: "disease",
      category: "biolink:Disease",
    },
    target: {
      id: "UPHENO:0001001",
      name: "phenotype",
      category: "PhenotypicFeature",
    },
    example: {
      id: "MONDO:0020066",
      name: "Ehlers-Danlos syndrome",
      category: "biolink:Disease",
    },
  },
  {
    source: { id: "SO:0000704", name: "gene", category: "biolink:Gene" },
    target: {
      id: "UPHENO:0001001",
      name: "phenotype",
      category: "PhenotypicFeature",
    },
    example: { id: "HGNC:3603", name: "FBN1", category: "biolink:Gene" },
  },
  {
    source: {
      id: "Reactome:R-GGA-167826",
      name: "model",
      category: "biolink:Pathway",
    },
    target: {
      id: "MONDO:0000001",
      name: "disease",
      category: "biolink:Disease",
    },
    example: {
      id: "MONDO:0008608",
      name: "Down syndrome",
      category: "biolink:Disease",
    },
  },
  {
    source: { id: "SO:0001060", name: "variant", category: "variant" },
    target: {
      id: "MONDO:0000001",
      name: "disease",
      category: "biolink:Disease",
    },
    example: {
      id: "MONDO:0009061",
      name: "cystic fibrosis",
      category: "biolink:Disease",
    },
  },
];
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  gap: 0.9em;
}
.label {
  font-weight: 500;
  text-align: center;
}

span {
  color: black;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;

  gap: 0.3rem;
  border-radius: 0.5rem;
}
.suggestion-line {
  display: inline-flex;
  align-items: center;

  border-radius: 0.375rem;
  background: #f3f3f3;
  color: #222;
  font-size: 0.95rem;
  text-decoration: none;
  transition: background 0.2s;
}

.clickable {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: 0.375rem;

  color: #222;

  text-decoration: none;
  transition: background 0.2s;
  &:hover {
    color: #0056b3;
  }
}
:deep(.clickable a) {
  color: #3885dd;

  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none !important;
}
</style>
