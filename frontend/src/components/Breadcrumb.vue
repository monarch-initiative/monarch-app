<template>
  <nav aria-label="breadcrumb">
    <ul class="breadcrumb">
      <li v-for="(crumb, index) in breadcrumbs" :key="index">
        <router-link v-if="index !== breadcrumbs.length - 1" :to="crumb.path">
          {{ crumb.label }}
        </router-link>
        <span v-else>{{ crumb.label }}</span>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const breadcrumbs = computed(() => {
  const matchedRoutes = route.matched;
  return matchedRoutes.map((r) => ({
    path: r.path,
    label: r.meta.breadcrumb || r.name, // Uses `meta.breadcrumb` or fallback to route name
  }));
});
</script>

<style scoped>
.breadcrumb {
  display: flex;
  padding: 0;
  gap: 8px;
  font-size: 14px;
  list-style: none;
}

.breadcrumb li {
  display: flex;
  align-items: center;
}

.breadcrumb li:not(:last-child)::after {
  margin-left: 8px;
  content: ">";
}

.breadcrumb a {
  color: #007bff;
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}
</style>
