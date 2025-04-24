<template>
  <div class="tag-wrapper">
    <span class="synonym-tag" v-for="(tag, index) in tags" :key="index">
      {{ tag }}
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  tags: string[];
}>();
</script>

<style scoped lang="scss">
.tag-wrapper {
  display: flex;
  flex-wrap: wrap;
  margin-top: 0.5rem;
  gap: 0.5rem;
}

.synonym-tag {
  display: inline-block;
  padding: 0.35em 0.9em;
  border: 1px solid #b2ebf2;
  border-radius: 999px;
  background-color: #e0f7fa;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  color: #006064;
  font-weight: 500;
  font-size: 0.85rem;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #e0f7fa;
    cursor: default;
  }
}
</style>
