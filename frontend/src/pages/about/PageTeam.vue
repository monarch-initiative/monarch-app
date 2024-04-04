<!--
  about team page

  all monarch-related team members and info about them
-->

<template>
  <!-- brief intro -->
  <AppSection>
    <AppHeading>Team</AppHeading>
    <p>
      Monarch is made possible thanks to a diverse and dedicated team of
      biologists, scientists, and programmers from various schools and
      institutes:
    </p>
    <div class="groups">
      <AppLink
        v-for="(group, index) in team"
        :key="index"
        :to="'#' + kebabCase(group.name)"
        :replace="true"
        >{{ group.name }}</AppLink
      >
    </div>
  </AppSection>

  <!-- list each group -->
  <AppSection v-for="(group, groupIndex) in team" :key="groupIndex" width="big">
    <AppHeading>
      {{ group.name }}
    </AppHeading>
    <AppGroup :name="group.name" :link="group.link" />
    <AppGallery :cols="group.name.includes('Alumni') ? 6 : 4">
      <template v-if="!group.type">
        <AppMember
          v-for="(member, memberIndex) in group.members"
          :key="memberIndex"
          :name="member.name"
          :role="'role' in member ? member.role : ''"
          :link="'link' in member ? member.link : ''"
          :no-image="group.name.includes('Alumni') ? true : undefined"
        />
      </template>
      <template v-else>
        <AppGroup
          v-for="(member, memberIndex) in group.members"
          :key="memberIndex"
          :name="member.name"
          :link="member.link"
        />
      </template>
    </AppGallery>
  </AppSection>

  <!-- funding sources -->
  <AppSection>
    <AppHeading>Funding</AppHeading>
    <ul>
      <li>
        OFFICE OF THE DIRECTOR, NATIONAL INSTITUTES OF HEALTH
        <br />
        <AppLink to="https://reporter.nih.gov/project-details/10173498">
          The Monarch Initiative: Linking diseases to model organism
          resources</AppLink
        >
        <br />
        2R24OD011883-10A1
      </li>
      <li>
        NATIONAL HUMAN GENOME RESEARCH INSTITUTE, Center of Excellence in Genome
        Sciences
        <br />
        <AppLink to="https://reporter.nih.gov/project-details/10448140">
          A phenomics-first resource for interpretation of variants
        </AppLink>
        <br />
        7RM1HG010860-02
      </li>
      <li>
        NATIONAL HUMAN GENOME RESEARCH INSTITUTE
        <br />
        <AppLink to="https://reporter.nih.gov/project-details/10269338">
          The Human Phenotype Ontology: Accelerating Computational Integration
          of Clinical Data for Genomics</AppLink
        >
        <br />
        1U24HG011449-01A1
      </li>
    </ul>
  </AppSection>
</template>

<script setup lang="ts">
import { kebabCase } from "lodash";
import AppGroup from "@/components/AppGroup.vue";
import AppMember from "@/components/AppMember.vue";
import team from "./team.json";
</script>

<style lang="scss" scoped>
$wrap: 800px;

.groups {
  display: grid;
  grid-template-columns: 1fr 1fr;
  justify-items: flex-start;
  width: 100%;
  gap: 10px;
  text-align: left;
}

@media (max-width: $wrap) {
  .groups {
    grid-template-columns: 1fr;
  }
}
</style>
