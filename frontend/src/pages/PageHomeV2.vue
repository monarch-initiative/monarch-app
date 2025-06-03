<template>
  <PageTitle
    id="home-page"
    title="What is the Monarch Initiative?"
    class="home-title"
  />

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
    <div class="custom-grid">
      <div v-for="(tool, id) in TOOL_LINKS" :key="id">
        <AppLink :to="tool.to">
          <AppIcon
            v-if="tool.icon"
            :tooltip="tool.tooltip"
            :aria-label="tool.tooltip"
            :icon="tool.icon"
            class="icon"
          />
        </AppLink>
      </div>
    </div>
  </AppSection>

  <AppSection width="big">
    <AppHeading :level="1">Explore Knowledge Graph Tools</AppHeading>
    <div class="custom-grid kg-tools">
      <template v-for="(tool, id) in KG_TOOL_LINKS" :key="id">
        <AppToolTile
          v-tooltip="tool.tooltip"
          :to="tool.to"
          :aria-label="tool.tooltip"
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
import { KG_TOOL_LINKS, TOOL_LINKS } from "@/data/toolEntityConfig";
</script>

<style lang="scss" scoped>
.section:last-of-type {
  margin-bottom: 3em;
  gap: 0;
}

.section:first-of-type {
  gap: 3em;
}

.custom-grid {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 60em;

  gap: 2em;
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
  flex: 1 1 7em;
  flex-direction: column;
  align-items: center;
  max-width: 100%;
}

.home-title {
  margin-top: 2em;
}

.icon {
  z-index: 2;
  position: relative;
  position: relative;
  width: 12em;
  height: 6em;

  cursor: pointer;
  transition: transform 0.2s ease;

  @media (max-width: 1000px) {
    width: 9em;
    height: 7em;
  }
}

.icon:hover {
  transform: scale(1.08);
}

a:focus,
.icon:focus {
  outline: none;
}

.kg-tools {
  margin-top: 2.5em;

  @media (max-width: 1000px) {
    gap: 2.5em;
  }
}
</style>
