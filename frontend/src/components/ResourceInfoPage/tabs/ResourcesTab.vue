<template>
  <AppSection v-if="resourceLinks.length" width="big">
    <div v-for="link in resourceLinks" :key="`${link.key}-${link.value}`">
      {{ formatLabel(link.key) }}:
      <AppLink :to="link.value" :no-icon="true" class="resource-link">
        {{ link.value }}
      </AppLink>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import AppLink from "@/components/AppLink.vue";
import AppSection from "@/components/AppSection.vue";
import { formatLabel, normalizeResourceLinks } from "../helpers/links";

const props = defineProps<{
  item: Record<string, any>;
}>();

const resourceLinks = normalizeResourceLinks(props.item?.see_also ?? {});
</script>

<style scoped lang="scss">
.resource-link {
  color: $theme;
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
}
</style>
