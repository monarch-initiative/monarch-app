<template>
  <table class="download-table">
    <thead>
      <tr>
        <th>Description</th>
        <th>Download</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(item, i) in items" :key="i">
        <td>{{ item.label }}</td>
        <td>
          <a :href="item.url" target="_blank" class="download-btn">Download</a>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import type { DownloadItem } from "@/data/downloads";

defineProps<{ items: DownloadItem[] }>();
</script>

<style scoped>
.download-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
  table-layout: fixed; /* Ensures consistent column widths */
}

.download-table th,
.download-table td {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  text-align: left;
}

.download-btn {
  display: inline-block;
  padding: 0.3rem 0.6rem;
  border-radius: 5px;
  background: hsl(185, 100%, 30%);
  color: #fff;
  font-weight: 500;
  text-decoration: none;
}

.download-btn:hover {
  border-color: #0d75d8;
}
</style>
