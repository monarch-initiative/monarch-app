<template>
  <AppSection>
    <AppHeading>Resources</AppHeading>
    <p>Resources and tools central to Monarch Initiative.</p>
    <p>
      The Monarch Initiative is an international consortium that leads key global standards and semantic data integration technologies. Monarch resources and integrated data are also foundational to many downstream applications and contexts; we work closely with a variety of stakeholders and resource-development communities to capture feedback and make improvements.
      To maximize utility and impact, the Monarch platform is composed of multiple open-source, open-access components. We promote provenance and transparency, enhanced use of standards and new technologies and improved data accessibility, end-user utility, and data submission. Below, we highlight a collection of our flagship projects. Learn more about the complete suite of Monarch resources on our organization's documentation pages.
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
