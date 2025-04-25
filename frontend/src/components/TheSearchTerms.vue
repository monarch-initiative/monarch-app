<template>
  <div class="suggestions">
    <span
      v-for="(s, i) in searchSuggestions"
      :key="i"
      class="term"
      role="link"
      tabindex="0"
      @click="goToEntity(s.id)"
      @keydown.enter="goToEntity(s.id)"
    >
      {{ s.term }}
    </span>
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
  justify-content: center;
  margin: 0.7em;
  gap: 1em;
}

.term {
  color: hsl(185, 100%, 30%);
  font-size: 0.95rem;
  cursor: pointer;
  &:hover {
    color: #0056b3;
  }
}
</style>
