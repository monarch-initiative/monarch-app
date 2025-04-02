<template>
  <div class="suggestions">
    <div class="tooltip-wrapper" v-for="(s, i) in suggestions" :key="i">
      <span class="tooltip-trigger">{{ s.label }}</span>
      <div class="tooltip-box">
        e.g: Explore the disease to phenotype relation for
        <span class="tooltip-suggestion" @click="$emit('select', s.term)">
          {{ s.term }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  suggestions: {
    label: string;
    term: string;
  }[];
}>();

defineEmits<{
  (e: "select", term: string): void;
}>();
</script>

<style lang="scss" scoped>
.suggestions {
  display: flex;
  margin: 1em;
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
  width: 40em;
  margin-top: 1px;
  padding: 8px;
  transform: translateX(-50%);
  border-radius: 6px;
  background-color: #e8e2e2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  color: #000;
  font-size: 0.8rem;
  line-height: 1.4;
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
