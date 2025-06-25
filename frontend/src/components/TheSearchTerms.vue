<template>
  <div class="suggestions">
    <AppNodeBadge
      v-for="terms in searchSuggestions"
      :key="terms.id"
      class="terms"
      :node="{ label: terms.term, id: terms.id, category: terms.category }"
      :icon="true"
    />
  </div>
</template>

<script setup lang="ts">
  import AppNodeBadge from '@/components/AppNodeBadge.vue';

  const searchSuggestions = [
    {
      term: 'Ehlers-Danlos syndrome',
      id: 'MONDO:0007523',
      category: 'biolink:Disease',
    },
    { term: 'Fanconi anemia', id: 'MONDO:0019391', category: 'biolink:Disease' },
    {
      term: 'Loeys-Dietz syndrome',
      id: 'MONDO:0018954',
      category: 'biolink:Disease',
    },
    {
      term: 'Atrial septal defect',
      id: 'HP:0001631',
      category: 'PhenotypicFeature',
    },
    {
      term: 'Wiedemann-Steiner syndrome',
      id: 'MONDO:0011518',
      category: 'biolink:Disease',
    },
    { term: 'Arachnodactyly', id: 'HP:0001166', category: 'PhenotypicFeature' },

    {
      term: 'heart',
      id: 'UBERON:0000948',
      category: 'biolink:AnatomicalEntity',
    },
    {
      term: 'vestibular organ',
      id: 'UBERON:0006585',
      category: 'biolink:AnatomicalEntity',
    },
    { term: 'HTT', id: 'HGNC:4851', category: 'biolink:Gene' },
    { term: 'FBN1', id: 'HGNC:3603', category: 'biolink:Gene' },
  ];
</script>

<style scoped lang="scss">
  .suggestions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
  }

  .terms {
    display: inline-flex;
    align-items: center;
    padding: 0.5rem 0.5rem;
    border-radius: 0.375rem;
    background: #f3f3f3;
    color: #222;
    font-size: 0.95rem;
    text-decoration: none;
    transition: background 0.2s;
  }

  .terms:hover {
    background: #e1e1e1;
  }

  :deep(.terms a) {
    color: rgb(90, 95, 95);
    font-weight: 600;
    font-size: 0.9em;
    text-decoration: none !important;
  }

  :deep(.terms svg) {
    --color: unset;
  }
</style>
