<!--
  entry point for entire app
-->

<template>
  <!-- display current route with no "scaffolding" (header/footer/etc) around it -->
  <template v-if="route.meta.bare">
    <router-view />
  </template>

  <template v-else-if="route.matched.length">
    <TheBanner v-if="apiName !== 'local'">
      {{ apiName }} This repository is under review for potential modification
      in compliance with Administration directives.
    </TheBanner>
    <TheBanner v-if="apiName !== 'prod'">
      This web app is the
      <strong v-if="apiName === 'local'">LOCAL VERSION</strong>
      <strong v-if="apiName === 'beta'">BETA VERSION</strong>
      <strong v-if="apiName === 'dev'">DEV VERSION</strong>
      of the
      <AppLink to="https://monarchinitiative.org"> Monarch Web App </AppLink>.
      Not all features are implemented yet. Please use the feedback form
      <AppIcon icon="comment" />
      &nbsp;on any page to tell us what you think!
    </TheBanner>
    <!-- <TheBanner v-else>
      This banner can be used to make announcements on the production version of the web app. 
      Uncomment this section and replace this text with your announcement as needed. 
      Disabling the banner is as simple as commenting out this section.
    </TheBanner> -->

    <TheHeader />
    <main>
      <router-view />
      <TheFloatButtons />
      <TheSnackbar />
    </main>
    <TheFooter />
  </template>
</template>

<script setup lang="ts">
import { watch } from "vue";
import { useRoute } from "vue-router";
import { apiName } from "@/api";
import TheFloatButtons from "@/components/TheFloatButtons.vue";
import TheFooter from "@/components/TheFooter.vue";
import TheHeader from "@/components/TheHeader.vue";
import { appDescription, appTitle, appUrl } from "@/global/meta";
import TheBanner from "./components/TheBanner.vue";
import TheSnackbar from "./components/TheSnackbar.vue";

/** route info */
const route = useRoute();

/** when route changes, update document metadata. see https://metatags.io/ */
watch(
  () => route,
  async () => {
    /**
     * meta vars set in components should override this, since this component is
     * root and renders first.
     */

    /** update document title from current route name */
    if (route.name) appTitle.value = [String(route.name) || ""];

    /** update description from current route meta */
    if (route.meta.description)
      appDescription.value = String(route.meta.description);

    /** update canonical url from current url in address bar */
    appUrl.value = window.location.href;
  },
  { immediate: true, deep: true },
);
</script>
