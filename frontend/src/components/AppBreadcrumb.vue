<template>
  <nav aria-label="breadcrumb" class="breadcrumb">
    <ul>
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

const props = defineProps<{
  dynamicBreadcrumb?: string;
}>();

const route = useRoute();

interface Breadcrumb {
  path: string;
  label: string;
}

const breadcrumbs = computed<Breadcrumb[]>(() => {
  const breadcrumbTrail: Breadcrumb[] = [{ path: "/", label: "Home" }];
  const matchedRoutes = route.matched;

  matchedRoutes.forEach((matchedRoute, index) => {
    const fullPath = matchedRoutes
      .slice(0, index + 1)
      .map((r) => r.path)
      .join("");

    let label = matchedRoute.meta.breadcrumb || matchedRoute.name || "Unknown";

    // Use dynamicBreadcrumb if available and we are at the last breadcrumb
    if (
      index === matchedRoutes.length - 1 &&
      props.dynamicBreadcrumb &&
      props.dynamicBreadcrumb.trim() !== ""
    ) {
      label = props.dynamicBreadcrumb;
    }

    breadcrumbTrail.push({
      path: fullPath,
      label: label as string,
    });
  });

  return breadcrumbTrail;
});
</script>

<style lang="scss" scoped>
$wrap: 1000px;
.breadcrumb {
  display: flex;
  flex-wrap: wrap;
  max-width: 100vw;
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
