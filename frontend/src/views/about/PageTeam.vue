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
      institutes.
    </p>
    <p>
      <template v-for="(group, index) in team" :key="index">
        <AppLink :to="'#' + kebabCase(group.name)">{{ group.name }}</AppLink>
        <span v-if="index !== team.length - 1"> · </span>
      </template>
    </p>
  </AppSection>

  <!-- list each group -->
  <AppSection v-for="(group, groupIndex) in team" :key="groupIndex" width="big">
    <AppHeading>
      {{ group.name }}
    </AppHeading>
    <AppGroup :name="group.name" :link="group.link" />
    <AppGallery v-if="!group.type">
      <AppMember
        v-for="(member, memberIndex) in group.members"
        :key="memberIndex"
        :name="member.name"
        :role="'role' in member ? member.role : ''"
        :link="member.link"
      />
    </AppGallery>
    <AppGallery v-else>
      <AppGroup
        v-for="(member, memberIndex) in group.members"
        :key="memberIndex"
        :name="member.name"
        :link="member.link"
      />
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
import AppMember from "@/components/AppMember.vue";
import team from "./team.json";
import AppGroup from "@/components/AppGroup.vue";
</script>
