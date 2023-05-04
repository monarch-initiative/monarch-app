<!--
  homepage of entire site
-->

<template>
  <!-- dive right in -->
  <AppSection design="fill">
    <AppTabs v-model="tab" name="Explore Mode" :tabs="tabs" route="Explore" />
    <NodeSearch />
  </AppSection>

  <AppSection>
    <AppHeading>What is Monarch?</AppHeading>

    <!-- high level description of monarch as a whole. "elevator pitch" -->
    <!-- eslint-disable-next-line -->
    <AppFlex gap="big" vAlign="top">
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
    </AppFlex>

    <hr />

    <!-- (rough) node counts, just for advertising -->
    <AppFlex>
      <!-- http://solr.monarchinitiative.org/solr/search/select?q=*:*&rows=0&facet=true&facet.field=category&wt=json -->
      <AppTile
        icon="category-gene"
        design="small"
        :title="`~${(1000000).toLocaleString()}`"
        subtitle="genes"
      />
      <AppTile
        icon="category-disease"
        design="small"
        :title="`~${(25000).toLocaleString()}`"
        subtitle="diseases"
      />
      <AppTile
        icon="category-phenotype"
        design="small"
        :title="`~${(70000).toLocaleString()}`"
        subtitle="phenotypes"
      />
      <AppTile
        icon="category-variant"
        design="small"
        :title="`~${(3000000).toLocaleString()}`"
        subtitle="variants"
      />
      <AppTile
        icon="category-genotype"
        design="small"
        :title="`~${(200000).toLocaleString()}`"
        subtitle="genotypes"
      />
      <AppTile
        icon="category-anatomy"
        design="small"
        :title="`~${(100000).toLocaleString()}`"
        subtitle="anatomies"
      />
      <AppTile
        icon="category-publication"
        design="small"
        :title="`~${(50000).toLocaleString()}`"
        subtitle="publications"
      />
      <AppTile
        icon="category-unknown"
        design="small"
        :title="`~${(5000000).toLocaleString()}`"
        subtitle="total nodes"
      />
    </AppFlex>
    <AppButton to="/about" text="Learn more" icon="arrow-right" />
  </AppSection>

  <!-- specific feature demos  -->

  <AppSection>
    <AppHeading>Highlights</AppHeading>

    <p>Some cool things you can do on this website.</p>

    <AppHighlight :src="nodeSearch">
      Quickly and easily browse nodes. Filter by category and taxon. See your
      recent and frequent searches.
    </AppHighlight>

    <AppHighlight :src="nodeSearch">
      Easily search our knowledge graph for multiple nodes from free text.
      Download the results or send them to the phenotype explorer tool for
      analysis.
    </AppHighlight>

    <AppHighlight :src="nodeSearch">
      Compare a set of phenotypes to another set of phenotypes, or to all
      genes/diseases of a species. See a rich comparison of the overlap between
      the two sets.
    </AppHighlight>

    <AppHighlight :src="nodeSearch">
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

    <AppFlex>
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
      <AppTile
        to="https://twitter.com/MonarchInit"
        icon="twitter"
        title="Twitter"
        subtitle="Quick updates and musings"
        design="small"
      />
      <AppTile
        to="https://genomic.social/@monarch_initiative"
        icon="mastodon"
        title="Mastodon"
        subtitle="Quick updates and musings"
        design="small"
      />
    </AppFlex>
  </AppSection>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { getBlogPosts } from "@/api/blog";
import AppHighlight from "@/components/AppHighlight.vue";
import AppPost from "@/components/AppPost.vue";
import AppTabs from "@/components/AppTabs.vue";
import AppTile from "@/components/AppTile.vue";
import { useQuery } from "@/util/composables";
import NodeSearch from "./explore/NodeSearch.vue";
import tabs from "./explore/tabs.json";
import nodeSearch from "@/assets/demos/node-search.mp4";
import textAnnotator from "@/assets/demos/text-annotator.mp4";
import phenotypeExplorer from "@/assets/demos/phenotype-explorer.mp4";
import nodePage from "@/assets/demos/node-page.mp4";

/** selected tab state */
const tab = ref(tabs[0].id);

const {
  query: getPosts,
  data: blogPosts,
  isLoading,
  isError,
} = useQuery(async function () {
  return await getBlogPosts();
}, []);

onMounted(getPosts);
</script>
