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
import "normalize.css";
import "@/global/icons";
import "@/global/styles.scss"; /** keep these last so they take priority */
import TheBanner from "./components/TheBanner.vue";
import TheHeader from "@/components/TheHeader.vue";
import TheFooter from "@/components/TheFooter.vue";
import TheFloatButtons from "@/components/TheFloatButtons.vue";
import TheSnackbar from "./components/TheSnackbar.vue";
import { appTitle, appDescription, appUrl } from "@/global/meta";

/** route info */
const route = useRoute();

/** when route changes, update document meta data. see https://metatags.io/ */
watch(
  () => route.fullPath,
  async () => {
    /**
     * meta vars set in components should override this, since this component is
     * root and renders first.
     */

    /** update document title from route */
    appTitle.value = [String(route.name)];

    /** update description */
    appDescription.value = route.meta.description as string;

    /** update canonical url */
    appUrl.value = window.location.href;
  }
);
</script>
