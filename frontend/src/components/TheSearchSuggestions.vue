<template>
  <div class="suggestions">
    <div v-for="(s, i) in searchSuggestions" :key="i" class="tooltip-wrapper">
      <span class="tooltip-trigger">{{ s.label }}</span>
      <div class="tooltip-box">
        {{ s.text }}
        <span
          class="tooltip-suggestion"
          role="button"
          tabindex="0"
          @click="$emit('select', s.term)"
          @keydown.enter="$emit('select', s.term)"
        >
          {{ s.term }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  (e: "select", term: string): void;
}>();

const searchSuggestions = [
  {
    label: "Disease to Phenotype",
    term: "Ehlers-Danlos syndrome",
    text: "e.g: Explore the disease to phenotype relation for",
  },
  {
    label: "Model to Disease",
    term: "Down syndrome",
    text: "e.g: Explore the model to disease relation for",
  },
  {
    label: "Variant to disease",
    term: "cystic fibrosis",
    text: "e.g: Explore the variant to disease relation for",
  },
  {
    label: "Gene to Phenotype",
    term: "FBN1",
    text: "e.g: Explore the gene to phenotype relation for",
  },
];
</script>

<style lang="scss" scoped>
.suggestions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  margin: 0.7em;
  gap: 1em;
}

.tooltip-wrapper {
  display: inline-flex;
  position: relative;
  flex-direction: column;
  align-items: center;
}

.tooltip-trigger {
  color: #007bff;
  font-size: 0.9rem;
  text-decoration: underline;
  cursor: pointer;
}

/* Tooltip box positioned directly under the trigger */
.tooltip-box {
  visibility: hidden;
  z-index: 999;
  position: absolute;
  top: 100%;
  left: 50%;
  width: max-content;
  max-width: 40em;

  padding: 8px;
  transform: translateX(-50%);
  border-radius: 6px;
  background-color: #e8e2e2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  color: #000;
  font-size: 0.8rem;
  line-height: 1.4;
  white-space: normal;
  opacity: 0;
  pointer-events: auto;
  transition: opacity 0.2s ease;
}

/* Keep tooltip open if hovering on wrapper OR box */
.tooltip-wrapper:hover .tooltip-box {
  visibility: visible;
  opacity: 1;
}

.tooltip-box::after {
  position: absolute;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 5px;
  border-style: solid;
  border-color: transparent transparent #e8e2e2 transparent;
  content: "";
}

.tooltip-suggestion {
  margin-left: 4px;
  color: hsl(185, 100%, 30%);
  text-decoration: underline;
  cursor: pointer;
}

.tooltip-suggestion:hover {
  color: #0056b3;
}
</style>
