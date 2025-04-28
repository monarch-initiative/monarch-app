<template>
  <div class="suggestions">
    <span class="examples-label">Examples:</span>
    <AppLink
      :to="`/${s.id}`"
      v-for="(s, i) in searchSuggestions"
      :key="i"
      class="app-link"
    >
      {{ s.term }}
    </AppLink>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();

const searchSuggestions = [
  { term: "Ehlers-Danlos syndrome", id: "MONDO:0007523" },
  { term: "Arachnodactyly", id: "HP:0001166" },
  { term: "vestibular organ", id: "UBERON:0006585" },
  { term: "FBN1", id: "HGNC:3603" },
];

const goToEntity = (id: string) => {
  router.push({ path: `/${encodeURIComponent(id)}` });
};
</script>

<style scoped lang="scss">
.suggestions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  width: 43em;
  gap: 1em;
}

.examples-label {
  color: #555;
  font-weight: 600;
  font-size: 0.95rem;
}

.term {
  color: hsl(185, 100%, 30%);
  font-size: 0.95rem;
  cursor: pointer;
  &:hover {
    color: #0056b3;
  }
}
.app-link {
  text-decoration: none;
}
</style>
