<template>
  <nav aria-label="breadcrumb">
    <ul class="breadcrumb">
      <li v-for="(crumb, index) in breadcrumbs" :key="index">
        <router-link v-if="index !== breadcrumbs.length - 1" :to="crumb.path">
          {{ crumb.label }}
        </router-link>
        <span v-else>
          {{ crumb.label }}
        </span>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
interface Breadcrumb {
  path: string;
  label: string;
}

const breadcrumbs = computed<Breadcrumb[]>(() => {
  const breadcrumbTrail: Breadcrumb[] = [{ path: "/", label: "Home" }];
  const matchedRoutes = route.matched;

  if (route.path === "/knowledge-graph") {
    breadcrumbTrail.push({ path: "/search", label: "Search" });
  } else {
    if (route.path.startsWith("/knowledge-graph")) {
      breadcrumbTrail.push({
        path: "/knowledge-graph",
        label: "Knowledge Graph",
      });
    }

    // Build the breadcrumb trail dynamically for the matched routes
    matchedRoutes.forEach((route, index) => {
      const fullPath = matchedRoutes
        .slice(0, index + 1)
        .map((r) => r.path)
        .join("");
      const label = route.meta.breadcrumb || route.name || "Unknown";
      breadcrumbTrail.push({
        path: fullPath,
        label: label as string,
      });
    });
  }

  return breadcrumbTrail;
});
</script>

<style lang="scss" scoped>
$wrap: 1000px;
.breadcrumb {
  display: flex;
  padding: 0;
  gap: 8px;
  font-size: 14px;
  list-style: none;
  @media (max-width: $wrap) {
    padding: 0.2em;
  }
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
  color: hsl(185, 100%, 30%);
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}
</style>
