<template>
  <AppBreadcrumb />
  <PageTitle id="our-story" title="Our Story" />
  <AppSection width="big" design="bare">
    <!-- Page Title -->
    <section>
      <p>
        Monarch is made possible thanks to a diverse and dedicated team of
        biologists, scientists, and programmers from various schools and
        institutes:
      </p>

      <div class="groups-container">
        <div class="group-box" v-for="i in 2" :key="i">
          <ul>
            <li
              v-for="(group, index) in team.slice(
                (i - 1) * (team.length / 2),
                i * (team.length / 2),
              )"
              :key="index"
            >
              <AppLink :to="'#' + kebabCase(group.name)" :replace="true">
                {{ group.name }}
              </AppLink>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <section
      v-for="(group, groupIndex) in team"
      :key="groupIndex"
      class="university-block"
      :id="kebabCase(group.name)"
    >
      <div class="university-header">{{ group.name }}</div>
      <div class="group-logo-wrapper">
        <AppGroup
          v-if="group.link"
          :name="group.name"
          :link="group.link"
          class="university-logo"
        />
      </div>

      <div class="members">
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
      </div>
    </section>
  </AppSection>
</template>
<script setup lang="ts">
import { kebabCase } from "lodash";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppGroup from "@/components/AppGroup.vue";
import AppMember from "@/components/AppMember.vue";
import AppSection from "@/components/AppSection.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import team from "@/data/team.json";
</script>
<style scoped lang="scss">
$wrap: 1000px;
html {
  scroll-behavior: smooth;
}

:root {
  scroll-padding-top: 90px;
}

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

.groups-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 1rem;
  gap: 3em;
  @media (max-width: $wrap) {
    gap: 1.5em;
  }
}

.group-box {
  width: 100%;
  max-width: 400px;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  background-color: rgba(166, 236, 242, 0.3411764706);
  ul {
    margin: 0;
    padding: 0;
    list-style: none;
    white-space: nowrap;

    li + li {
      margin-top: 0.5rem;
    }

    a {
      color: #111;
      font-weight: normal;
      text-decoration: underline;
    }
  }
}

@media (min-width: $wrap) {
  .group-box {
    flex: 1;
  }
}

.university-block {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.university-header {
  width: 100%;
  padding: 0.6rem;
  background-color: rgba(166, 236, 242, 0.3411764706);
  font-weight: bold;
  font-size: 1.2rem;
  text-align: center;
}

.university-logo {
  display: block;
  max-height: 60px;
  margin: 1.5rem auto;
}
.group-logo-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 2em;
}
</style>
