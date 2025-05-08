<template>
  <PageTitle id="home" title="What is Monarch Initiative?" class="home-title" />
  <AppSection width="big">
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
    <AppHeading :level="1">Explore Monarch Initiative Tools</AppHeading>
    <div class="custom-grid">
      <template v-for="(tool, idx) in TOOL_LINKS" :key="idx">
        <AppToolTile
          v-tooltip="tool.tooltip"
          :to="tool.to"
          :icon="tool.icon"
          :title="tool.label"
        />
      </template>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import AppToolTile from "@/components/AppToolTile.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import { TOOL_LINKS } from "@/data/toolConfig";
</script>

<style lang="scss" scoped>
.section:last-of-type {
  margin-bottom: 3em;
}
.custom-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(7em, 1fr));
  align-items: center;
  width: 100%;
  gap: 1.5rem;
}

@media (max-width: 1000px) {
  .custom-grid {
    grid-template-rows: repeat(2, auto);
    grid-auto-columns: minmax(7em, 1fr);
    grid-auto-flow: column;
  }
}

@media (max-width: 600px) {
  .custom-grid {
    grid-template-rows: auto;
    grid-template-columns: 1fr;
    grid-auto-flow: row;
  }
}

.custom-grid > * {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.home-title {
  margin-top: 2em;
}
</style>
