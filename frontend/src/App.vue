<!--
  entry point for entire app
-->

<template>
  <TheBanner />
  <TheHeader />
  <main>
    <router-view />
    <TheFloatButtons />
    <TheSnackbar />
  </main>
  <TheFooter />
</template>

<script setup lang="ts">
import { watch } from "vue";
import { useRoute } from "vue-router";
import TheFloatButtons from "@/components/TheFloatButtons.vue";
import TheFooter from "@/components/TheFooter.vue";
import TheHeader from "@/components/TheHeader.vue";
import { appDescription, appTitle, appUrl } from "@/global/meta";
import TheBanner from "./components/TheBanner.vue";
import TheSnackbar from "./components/TheSnackbar.vue";

/** route info */
const route = useRoute();

/** when route changes, update document meta data. see https://metatags.io/ */
watch(
  () => route,
  async () => {
    /**
     * meta vars set in components should override this, since this component is
     * root and renders first.
     */

    /** update document title from route */
    appTitle.value = [String(route.name) || ""];

    /** update description */
    appDescription.value = String(route.meta.description);

    /** update canonical url */
    appUrl.value = window.location.href;
  },
  { immediate: true, deep: true }
);
</script>
