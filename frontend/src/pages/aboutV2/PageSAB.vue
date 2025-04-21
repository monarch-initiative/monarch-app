<template>
  <AppBreadcrumb />
  <ThePageTitle id="about-sab" title="Scientific Advisory Board Members" />

  <AppSection design="bare" width="big" class="container">
    <div class="divider">
      <hr class="line left" />
      <hr class="line right" />
    </div>

    <p class="description">
      A priority of the Monarch Initiative is to base all research activities on
      sound scientific data, analyses, and interpretations. The Scientific
      Advisory Board (SAB) allows Monarch to receive peer review and advice
      designed to make a positive difference in the production and use of
      Monarch’s scientific products.
    </p>

    <AppGallery :cols="2" class="custom-gallery">
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
  padding-top: unset;
  gap: 4em;
}
.section.big[data-v-d078f057] {
  padding-top: unset;
}
.divider {
  position: relative;
  width: 100%;
  height: 1px;
  margin: 0 auto 1rem;
}

.line {
  position: absolute;
  top: 50%;
  width: 80%;
  border: none;
  border-top: 1px solid #000;
}

.line.left {
  left: 0;
}

.line.right {
  top: 0.4rem;
  right: 0;
}

@media (max-width: 600px) {
  .line {
    width: 80%;
  }
}
@media (max-width: 800px) {
  .custom-gallery {
    --screen-cols: 1 !important;
  }
}

.description {
  font-size: 1em;
}
</style>
