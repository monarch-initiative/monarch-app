<template>
  <PageTitle
    id="home-page"
    title="What is Monarch Initiative?"
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
            v-tooltip="tool.tooltip"
            :icon="tool.icon"
            class="icon"
          />
        </AppLink>
      </div>
    </div>
  </AppSection>

  <AppSection width="big">
    <AppHeading :level="1">Explore Knowledge Graph Tools</AppHeading>
    <div class="custom-grid">
      <template v-for="(tool, id) in KG_TOOL_LINKS" :key="id">
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
import { KG_TOOL_LINKS, TOOL_LINKS } from "@/data/toolEntityConfig";
</script>

<style lang="scss" scoped>
.section:last-of-type {
  margin-bottom: 3em;
  padding-top: 0;
}
.custom-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(7em, 1fr));
  align-items: center;
  justify-items: center;
  width: 100%;
  max-width: 60em;
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

.icon {
  z-index: 2;
  position: relative;
  width: 12em;
  height: 12em;
  border-radius: 50em;
  cursor: pointer;
  transition: transform 0.2s ease;

  @media (max-width: 1000px) {
    width: 9em;
    height: 9em;
  }
}

.icon:hover {
  transform: scale(1.08);
}

a:focus,
.icon:focus {
  outline: none;
}
</style>
