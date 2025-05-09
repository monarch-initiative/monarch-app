<template>
  <div class="container">
    <hr />
    <p class="label">Examples of relationships you can explore</p>
    <div class="suggestions">
      <div
        v-for="(search, i) in searchSuggestions"
        :key="i"
        class="suggestion-pair clickable"
        role="button"
        tabindex="0"
        @click="handleSuggestionClick(search.source.name)"
        @keydown.enter="handleSuggestionClick(search.source.name)"
      >
        <AppNodeBadge :node="search.source" :icon="true" class="badge" />
        <AppNodeBadge :node="search.target" :icon="true" class="badge" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick } from "vue";
import { useRouter } from "vue-router";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import { ENTITY_MAP } from "@/data/toolEntityConfig";

const router = useRouter();
defineEmits<{
  (e: "select", nodeId: string): void;
}>();

const searchSuggestions = [
  {
    source: {
      id: "MONDO:0020066",
      name: "Ehlers-Danlos syndrome",
      category: "biolink:Disease",
    },
    target: {
      id: "FYPO:0000001",
      name: "phenotype",
      category: "PhenotypicFeature",
    },
  },
  {
    source: {
      id: "HGNC:3603",
      name: "FBN1 ",
      category: "biolink:Gene",
    },
    target: {
      id: "SO:0000704",
      name: "Gene",
      category: "gene",
    },
  },
  {
    source: {
      id: "MONDO:0008608",
      name: "Down syndrome ",
      category: "biolink:Disease",
    },
    target: {
      id: "MONDO:0000001",
      name: "Models",
      category: "model",
    },
  },
  {
    source: {
      id: "MONDO:0009061",
      name: "cystic fibrosis ",
      category: "biolink:Disease",
    },
    target: {
      id: "MONDO:0000001",
      name: "Variants",
      category: "variant",
    },
  },
];

function scrollToHashWithOffset(hash: string, offset = 80) {
  const el = document.querySelector(hash);
  if (el) {
    const y = el.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo({ top: y, behavior: "smooth" });
  }
}

const handleSuggestionClick = async (name: string) => {
  const entity = ENTITY_MAP[name];

  if (entity?.id) {
    await router.push({ path: "/" + entity.id, hash: "#" + entity.to });
    await nextTick();
    setTimeout(() => {
      scrollToHashWithOffset(`#${entity.to}`, 80);
    }, 1000);
  }
};
</script>

<style lang="scss" scoped>
$wrap: 1000px;
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  gap: 0.6em;

  @media (max-width: $wrap) {
    width: 100%;
    gap: 0.3em;
  }
}
.label {
  font-weight: 600;
  text-align: center;
}

span {
  color: black;
  white-space: nowrap;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  width: 100%;

  margin: 0 auto;
  gap: 0.5rem;
}

.suggestion-pair {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  gap: 0.6rem;
  border-radius: 0.5rem;
  background: #f3f3f3;
  white-space: nowrap;
  cursor: pointer;
  transition: background 0.2s ease;

  &:hover {
    background: #e0e0e0;
  }
}

.badge {
  font-weight: 600;
}

.clickable {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: 0.375rem;
  color: #3885dd;
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
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
  white-space: nowrap;
  &:hover {
    color: #0056b3;
  }
}

.example {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding-left: 0.4em;
  white-space: nowrap;
}
</style>
