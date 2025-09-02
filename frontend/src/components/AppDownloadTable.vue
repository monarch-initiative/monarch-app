<template>
  <table class="download-table">
    <tbody>
      <tr v-for="(item, i) in items" :key="i">
        <td>
          <div class="row-content">
            <span class="label">{{ item.label }}</span>
            <AppButton text="Download" :to="item.url" design="circle" />
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import type { DownloadItem } from "@/data/downloads";
import AppButton from "./AppButton.vue";

const { items } = withDefaults(defineProps<{ items?: DownloadItem[] }>(), {
  items: () => [],
});
</script>

<style scoped>
.download-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.download-table td {
  padding: 0.75rem 1rem;
  border: 1px solid #e0e0e0;
}

.row-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.label {
  font-weight: 500;
}
</style>
