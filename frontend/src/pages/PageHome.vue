<!--
  homepage of entire site
-->

<template>
  <!-- dive right in -->
  <AppSection design="fill">
    <div class="explore">Explore our knowledge on this website</div>
    <AppTabs
      v-model="tab"
      name="Explore Mode"
      :tabs="tabs"
      navigate="Explore"
    />
    <TabSearch :minimal="true" :focus-explore="true" />
  </AppSection>

  <AppSection>
    <AppHeading>What is Monarch?</AppHeading>

    <!-- high level description of monarch as a whole. "elevator pitch" -->
    <!-- eslint-disable-next-line -->
    <div class="tiles">
      <AppTile
        icon="people"
        title="For informaticians, patients, clinicians, researchers, and more"
      />
      <AppTile
        icon="knowledge-graph"
        title="An extensive, cross-species, semantic knowledge graph"
      />
      <AppTile
        icon="phenotype-search"
        title="A website for quick and easy exploration of the graph"
      />
      <AppTile
        icon="toolbox"
        title="Powerful API and ecosystem of related tools"
      />
    </div>

    <hr />

    <!-- KG counts (for advertising) -->
    <AppFlex gap="medium">
      <!-- node counts -->
      <AppTile
        v-for="(item, index) in metadata.node"
        :key="index"
        :icon="item.icon"
        :title="startCase(item.label.replace(/biolink:/g, ''))"
        :subtitle="`~${item.count.toLocaleString()}`"
        design="small"
      />
      <!-- association counts -->
      <AppTile
        v-for="(item, index) in metadata.association"
        :key="index"
        :icon="item.icon"
        :title="startCase(item.label.replace(/biolink:/g, ''))"
        :subtitle="`~${item.count.toLocaleString()}`"
        design="small"
      />
    </AppFlex>
    <AppButton to="/about" text="Learn more" icon="arrow-right" />
  </AppSection>

  <!-- specific feature demos  -->

  <AppSection>
    <AppHeading>Highlights</AppHeading>

    <p>Some cool things you can do on this website.</p>

    <AppHighlight :src="search">
      Quickly and easily browse nodes. Filter by category and taxon. See your
      recent and frequent searches.
    </AppHighlight>

    <AppHighlight :src="textAnnotator">
      Easily search our knowledge graph for multiple nodes from free text.
      Download the results or send them to the phenotype explorer tool for
      analysis.
    </AppHighlight>

    <AppHighlight :src="phenotypeExplorer">
      Compare a set of phenotypes to another set of phenotypes, or to all
      genes/diseases of a species. See a rich comparison of the overlap between
      the two sets.
    </AppHighlight>

    <AppHighlight :src="nodePage">
      See rich details about each node. Traverse between nodes via associations
      between them, and view the evidence for those associations.
    </AppHighlight>
  </AppSection>

  <!-- news -->
  <AppSection>
    <AppHeading>News</AppHeading>

    <p>Latest posts about Monarch.</p>

    <!-- status -->
    <AppStatus v-if="isLoading" code="loading">Loading posts</AppStatus>
    <AppStatus v-if="isError" code="error">Error loading posts</AppStatus>

    <!-- list of posts -->
    <AppFlex v-if="blogPosts.length" direction="col" gap="big">
      <AppPost
        v-for="(item, index) in blogPosts.slice(0, 5)"
        :key="index"
        class="blog-post"
        :image="item.thumbnail"
        :date="item.date"
        :link="item.link"
        :title="item.title"
        :description="item.description"
      />
    </AppFlex>

    <AppButton
      to="https://monarchinit.medium.com/"
      text="More on Medium"
      icon="medium"
    />
  </AppSection>

  <!-- social media -->
  <AppSection>
    <AppHeading>Follow</AppHeading>

    <p>Be the first to know when we have major updates or other fun news.</p>

    <AppFlex align-v="top">
      <AppTile
        to="https://medium.com/@MonarchInit"
        icon="medium"
        title="Medium"
        subtitle="Blog posts and major updates"
        design="small"
      />
      <AppTile
        to="https://github.com/monarch-initiative"
        icon="github"
        title="GitHub"
        subtitle="Source code and releases"
        design="small"
      />
    </AppFlex>
  </AppSection>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { startCase } from "lodash";
import { getBlogPosts } from "@/api/blog";
import nodePage from "@/assets/demos/node-page.mp4";
import phenotypeExplorer from "@/assets/demos/phenotype-explorer.mp4";
import search from "@/assets/demos/search.mp4";
import textAnnotator from "@/assets/demos/text-annotator.mp4";
import AppHighlight from "@/components/AppHighlight.vue";
import AppPost from "@/components/AppPost.vue";
import AppTabs from "@/components/AppTabs.vue";
import AppTile from "@/components/AppTile.vue";
import { useQuery } from "@/util/composables";
import tabs from "./explore/tabs.json";
import TabSearch from "./explore/TabSearch.vue";
import metadata from "./metadata.json";

/** selected tab state */
const tab = ref(tabs[0].id);

const {
  query: runGetBlogPosts,
  data: blogPosts,
  isLoading,
  isError,
} = useQuery(async function () {
  return await getBlogPosts();
}, []);

onMounted(runGetBlogPosts);
</script>

<style lang="scss" scoped>
$wrap: 600px;

.tiles {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
}

.explore {
  color: $off-black;
}

@media (max-width: $wrap) {
  .tiles {
    grid-template-columns: 1fr;
  }
}
</style>
