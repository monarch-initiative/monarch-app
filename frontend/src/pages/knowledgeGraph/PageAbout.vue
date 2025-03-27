<template>
  <AppBreadcrumb />
  <!-- <AppSection width="big" class="section" design="bare"> -->

  <PageTitle
    id="kg-about"
    title="KnowledgeGraph"
    tagline="Discover the power of our Knowledge Graph, seamlessly connecting
biological data to reveal hidden relationships."
    image-src="/icons/monarch-logo.svg"
  />

  <!--WHat is KG-->
  <AppSection width="big" design="bare" class="section kg-about">
    <AppHeading class="fullWidthHeader">What is KnowledgeGraph?</AppHeading>
    <div class="content-container">
      <div class="text-column">
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
          minim veniam, quis nostrud exercitation ullamco laboris nisi ut
          aliquip ex ea commodo consequat. Duis aute irure dolor in
          reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
          pariatur. Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet,
          consectetur adipiscing elit. Ut enim ad minim veniam, quis nostrud
          exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
          Duis aute irure dolor in reprehenderit in voluptate velit esse cillum
          dolore eu fugiat nulla pariatur. Lorem ipsum dolor sit amet,Lorem
          ipsum dolor sit amet, consectetur adipiscing elit
        </p>
      </div>

      <iframe
        title="What is KnowledgeGraph?"
        class="video"
        src="https://www.youtube.com/embed/z11xZKBEO-U"
        frameborder="0"
        allow="autoplay; picture-in-picture"
        allowfullscreen
      ></iframe>
    </div>
  </AppSection>

  <!--Entity and Association statistics-->
  <AppSection width="big" design="bare">
    <div class="enity-association">
      <AppHeading :level="2">Entity and Association Statistics</AppHeading>
      <AppGallery :cols="4">
        <!-- node counts -->
        <AppTile
          v-for="(item, index) in metadata.node"
          :key="index"
          :icon="item.icon"
          :title="startCase(item.label.replace(/biolink:/g, ''))"
          :subtitle="formatNumber(item.count, true)"
          design="small"
        />
        <!-- association counts -->
        <AppTile
          v-for="(item, index) in metadata.association"
          :key="index"
          :icon="item.icon2 ? undefined : item.icon"
          :title="startCase(item.label.replace(/biolink:/g, ''))"
          :subtitle="formatNumber(item.count, true)"
          design="small"
        >
          <AppFlex v-if="item.icon2" gap="tiny" class="association">
            <AppIcon :icon="item.icon" />
            <svg viewBox="0 0 9 2" class="line">
              <line x1="0" y1="1" x2="9" y2="1" />
            </svg>
            <AppIcon :icon="item.icon2" />
          </AppFlex>
        </AppTile>
      </AppGallery>
    </div>
  </AppSection>

  <!--KG's Tools and Resources-->
  <AppSection width="big" design="bare" class="section">
    <AppHeading class="fullWidthHeader"
      >Knowledge Graph's Tools and Resources</AppHeading
    >
    <AppFlex gap="big" class="tools">
      <AppTileCard
        title="Graph"
        content="Dive into the Monarch Knowledge Graph, where complex biological data is interconnected. This section lets you explore relationships between genes, diseases, phenotypes, and more, providing deep insights to accelerate scientific discovery."
        button-text="Explore"
      />

      <AppTileCard
        title="Phenotype Explore"
        content="The Phenotype Explorer enables you to investigate phenotypic data, linking observable traits to genetic information. Use this tool to explore how phenotypes are connected to genetic variations and their role in diseases."
        button-text="Explore"
      />
      <AppTileCard
        title="Text Annotator"
        content="The Text Annotator is a powerful tool for extracting biological knowledge from scientific literature. It helps researchers identify key biological concepts and relationships within text, enhancing the search for relevant data and insights."
        button-text="Explore"
      />

      <AppTileCard
        title="Tools"
        content="Access a wealth of resources that support your research, including tools, datasets, and documentation. This section provides the essential data and information needed to make the most of Monarch's integrated biological knowledge"
        button-text="Explore"
      />
    </AppFlex>
  </AppSection>

  <!--Title Placeholder - Has to be replaced with real content-->
  <AppSection width="big" class="section" design="bare">
    <AppHeading class="fullWidthHeader">Title Placeholder</AppHeading>
    <p>
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod
      tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
      veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
      commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
      velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
      cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id
      est laborum.
    </p>
    <iframe
      title="Monarch Initiative: Resource Overview"
      class="ORIP-video"
      src="https://www.youtube.com/embed/25e88kbjKtU?si=lG88-c2fZcKHxIhm"
      frameborder="0"
      allow="autoplay; picture-in-picture"
      allowfullscreen
    ></iframe>
  </AppSection>

  <!--contact-->
  <AppSection width="big" design="bare">
    <p class="info">
      If you have any questions, feel free to reach out to us at :
      <a>info@monarchinitiative.org</a>
    </p></AppSection
  >
</template>

<script setup lang="ts">
import { startCase } from "lodash";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppHeading from "@/components/AppHeading.vue";
import AppSection from "@/components/AppSection.vue";
import AppTileCard from "@/components/AppTileCard.vue";
import PageTitle from "@/components/PageTitle.vue";
import metadata from "@/pages/explore/metadata.json";
import { formatNumber } from "@/util/string";
</script>

<style lang="scss" scoped>
$wrap: 1000px;

.section.big {
  padding-bottom: unset;
}

.fullWidthHeader {
  width: 100%;
  padding: 0.6em 0.5em;
  background-color: #e0e0e0;
  color: black;
  text-align: left;
}

.content-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4em;

  p {
    line-height: 1.6;
    text-align: left;
  }
  @media (max-width: $wrap) {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    gap: 1.3em;
  }
}

.text-column {
  flex: 1;
  max-width: 50%;
  overflow: hidden;
  @media (max-width: $wrap) {
    max-width: 100%;
  }
}

iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.video {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  aspect-ratio: 16 / 9;
  width: 100%;
  max-width: 45%;
  height: 100%;

  @media (max-width: $wrap) {
    width: 100%;
    min-width: 380px;
    max-width: 80%;
  }
}

.enity-association {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 2em;
  gap: 3em;
  background-color: #a6ecf257;
}
.ORIP-video {
  aspect-ratio: 16 / 9;
  width: 65%;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
  @media (max-width: $wrap) {
    width: 100%;
    min-width: 380px;
    max-width: 80%;
  }
}

.association {
  font-size: 2rem;
}

h1 {
  padding: 0;
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
.tools {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  width: 100%;

  @media (max-width: 1100px) {
    flex-direction: column;
    width: 100%; /* Ensure it still takes full width in column mode */
  }
}

.info {
  padding: 1em;
}

.section.center {
  gap: 1em;
  @media (max-width: $wrap) {
    gap: 1.5em;
  }
}

.kg-about[data-v-55956969] {
  @media (max-width: $wrap) {
    padding-top: 0.7em;
  }
}
</style>
