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

  if (route.path === "/kg") {
    breadcrumbTrail.push({ path: "/search", label: "Search" });
  } else {
    if (route.path.startsWith("/kg")) {
      breadcrumbTrail.push({
        path: "/kg",
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
  flex-wrap: wrap;
  margin: 1em;
  padding: 0;
  gap: 0.25em; // Tighter gap for mobile
  font-size: 0.9em;
  line-height: 1.4;
  list-style: none;
}

.breadcrumb li {
  display: inline-flex;
  align-items: center;
  margin: unset;
  white-space: nowrap;

  &:not(:last-child)::after {
    margin-right: 0.25em;
    margin-left: 0.25em;
    content: ">";
    color: #888;
  }
}

.breadcrumb a {
  color: hsl(185, 100%, 30%);
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.breadcrumb span {
  color: #000;
  font-weight: 500;
}
</style>
