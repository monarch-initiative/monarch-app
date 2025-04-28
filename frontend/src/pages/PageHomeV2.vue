<!--
  homepage of entire site
-->

<template>
  <AppSection width="big">
    <PageTitle id="home" title="What is Monarch Initiative" />
    <p>
      The Monarch Initiative is an international consortium that leads key
      global standards and semantic data integration technologies. Monarch
      resources and integrated data are also foundational to many downstream
      applications and contexts; we work closely with a variety of stakeholders
      and resource-development communities to capture feedback and make
      improvements. To maximize utility and impact, the Monarch platform is
      composed of multiple open-source, open-access components. We promote
      provenance and transparency, enhanced use of standards and new
      technologies and improved data accessibility, end-user utility, and data
      submission. Learn more about the complete suite of Monarch resources on
      our organization's documentation pages.
    </p>
  </AppSection>

  <AppSection width="big">
    <AppGallery>
      <template v-for="category in resources" :key="category">
        <AppTile
          v-for="(resource, resourceIndex) in category"
          :key="resourceIndex"
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
import AppTile from "@/components/AppTile.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import resources from "./resources.json";
</script>

<style lang="scss" scoped>
.association {
  font-size: 2rem;
}

.video {
  aspect-ratio: 16 / 9;
  width: 100%;
}

.line {
  width: 10px;

  line {
    stroke: currentColor;
    stroke-width: 2;
    stroke-dasharray: 1 3;
    stroke-linecap: round;
  }
}
</style>
