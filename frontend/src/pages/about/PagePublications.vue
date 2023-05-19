<!--
  about publications page

  list of publication and other works related to monarch, sorted by year
-->

<template>
  <AppSection>
    <AppHeading>Publications</AppHeading>
    <p>
      <template v-for="(group, index) in publications" :key="index">
        <AppLink :to="'#' + group.year">{{ group.year }}</AppLink>
        <span v-if="index !== publications.length - 1"> · </span>
      </template>
    </p>
  </AppSection>

  <!-- by year -->
  <AppSection v-for="(group, index) in publications" :key="index" width="big">
    <AppHeading>{{ group.year }}</AppHeading>
    <AppGallery size="big">
      <AppCitation
        v-for="(publication, item) in group.list"
        :key="item"
        :title="publication.title"
        :authors="publication.authors"
        :details="[publication.journal, publication.issue, publication.link]"
      />
    </AppGallery>
  </AppSection>
</template>

<script setup lang="ts">
import AppCitation from "@/components/AppCitation.vue";
import publications from "./publications.json";
</script>
