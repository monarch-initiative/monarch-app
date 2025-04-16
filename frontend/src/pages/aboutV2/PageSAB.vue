<template>
  <AppBreadcrumb />
  <ThePageTitle id="about-sab" title="Scientific Advisory Board Members" />
  <div class="divider">
    <hr class="top-line" />
    <hr class="bottom-line" />
  </div>
  <AppSection design="bare" width="big" class="container">
    <p class="description">
      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum
      dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
      proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
      Curabitur pretium tincidunt lacus. Nulla gravida orci a odio.Excepteur
      sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt
      mollit anim id est laborum. Curabitur pretium tincidunt lacus. Nulla
      gravida orci a odio
    </p>

    <AppGallery :cols="2">
      <AppMemberCard
        v-for="(member, index) in sab.members"
        :key="index"
        :name="member.name"
        :role="member.description || member.descripion"
        :link="member.link"
      />
    </AppGallery>
  </AppSection>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppMemberCard from "@/components/AppMemberCard.vue";
import ThePageTitle from "@/components/ThePageTitle.vue";
import sab from "@/data/sab.json";
</script>

<style>
.section[data-v-d078f057]:last-of-type {
  margin: 3em;
  gap: 4em;
}
.divider {
  width: 100%;
}
.top-line {
  left: 0;
  margin-left: 15em;
}
.bottom-line {
  right: 0;
  margin: 1.8em 15em;
}
.top-line,
.bottom-line {
  position: absolute;
  max-width: 60%;
  border-top: 1px solid #000;
}

.description {
  font-size: 0.9em;
}
</style>
