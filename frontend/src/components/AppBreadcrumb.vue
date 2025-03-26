<template>
  <nav aria-label="breadcrumb">
    <ul class="breadcrumb">
      <li v-for="(crumb, index) in breadcrumbs" :key="index">
        <router-link
          v-if="index !== breadcrumbs.length - 1 && !crumb.disabled"
          :to="crumb.path"
        >
          {{ crumb.label }}
        </router-link>
        <span v-else :class="{ 'breadcrumb-disabled': crumb.disabled }">
          {{ crumb.label }}
        </span>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

// Access the current route
const route = useRoute();

// Define the type for each breadcrumb item
interface Breadcrumb {
  path: string;
  label: string;
  disabled?: boolean;
}

const breadcrumbs = computed<Breadcrumb[]>(() => {
  const matchedRoutes = route.matched;
  let breadcrumbTrail: Breadcrumb[] = [];

  // Always add the "Home" breadcrumb as the first item
  breadcrumbTrail.push({
    path: "/",
    label: "Home",
  });

  if (route.path.includes("/knowledge-graph")) {
    breadcrumbTrail.push({
      path: "/knowledge-graph",
      label: "Knowledge Graph",
      disabled: true,
    });
  }

  // Build breadcrumb trail based on URL
  matchedRoutes.forEach((route, index) => {
    const fullPath = matchedRoutes
      .slice(0, index + 1)
      .map((r) => r.path)
      .join("");
    const label = route.meta.breadcrumb || route.name || "Unknown";
    breadcrumbTrail.push({
      path: fullPath,
      label: label as string, // Ensure the label is a string
    });
  });

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
  color: #007bff;
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

/* Style for disabled breadcrumb */
.breadcrumb-disabled {
  color: #6c757d; /* Grey color */
  text-decoration: none; /* Prevent underline */
  cursor: not-allowed; /* Show "not-allowed" cursor */
}
</style>
