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
        <span class="node">
          <AppIcon
            class="icon"
            :icon="getCategoryIcon(search.source.category)"
          />
          <AppNodeText :text="search.source.name" />
        </span>
        <span class="node">
          <AppIcon
            class="icon"
            :icon="getCategoryIcon(search.target.category)"
          />
          <AppNodeText :text="search.target.name" />
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick } from "vue";
import { useRouter } from "vue-router";
import { getCategoryIcon, getCategoryLabel } from "@/api/categories";
import AppNodeText from "@/components/AppNodeText.vue";
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
      name: "Phenotype",
      category: "PhenotypicFeature",
    },
  },
  {
    source: {
      id: "HGNC:3603",
      name: "FBN1",
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
      id: "Reactome:R-GGA-167826",
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
  let attempts = 0;
  const maxAttempts = 30;
  let lastY = -1;

  const tryScroll = () => {
    const el = document.querySelector(hash);
    if (!el) {
      if (attempts++ < maxAttempts) {
        requestAnimationFrame(tryScroll);
      } else {
        console.warn(`Element ${hash} not found after ${maxAttempts} attempts`);
      }
      return;
    }

    const y = el.getBoundingClientRect().top + window.scrollY - offset;

    // check if element has settled
    if (Math.abs(y - lastY) <= 2 || attempts > maxAttempts) {
      window.scrollTo({ top: y, behavior: "smooth" });
    } else {
      lastY = y;
      attempts++;
      requestAnimationFrame(tryScroll);
    }
  };

  requestAnimationFrame(tryScroll);
}

const handleSuggestionClick = async (name: string) => {
  const entity = ENTITY_MAP[name.trim()];
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
  pointer-events: none;
}
span {
  color: rgb(90, 95, 95);
}

.clickable {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: 0.375rem;

  font-weight: 500;
  font-size: 0.95em;
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

.icon {
  position: relative;
  top: -1px;
  margin-right: 0.4em;
  vertical-align: middle;
}
</style>
