<template>
  <AppSection>
    <AppHeading>Resources</AppHeading>
    <p>
      Resources and tools central to Monarch Initiative.
    </p>
  </AppSection>
  <AppSection
    v-for="(category, categoryIndex) in resources"
    :key="categoryIndex"
    width="big"
  >
    <AppHeading>
      {{ categoryIndex }}
    </AppHeading>
    <AppGallery :cols="3">
      <template
        v-for="(resource, resourceIndex) in category"
        :key="resourceIndex"
      >
        <AppTile
          :to="resource.link"
          :icon="resource.icon"
          :title="resource.name"
          :subtitle="resource.description"
        />
      </template>
    </AppGallery>
  </AppSection>
</template>

<script setup lang="ts">
// import { ref, watch } from "vue";
// import { kebabCase } from "lodash";
import resources from "./resources.json";

// type Props = {
//   name: string;
//   icon?: string;
//   link?: string;
// };

// const props = defineProps<Props>();

// const src = ref("");
// watch(
//   () => props.name,
//   async () => {
//     const icon = kebabCase((props.name || "").toLowerCase());
//     try {
//       src.value = (await import(`../../assets/icons/resource-${icon}.svg`)).default;
//     } catch (error) {
//       src.value = (await import(`../../assets/icons/toolbox.svg`)).default;
//     }
//   },
//   { immediate: true },
// );
</script>
