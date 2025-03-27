<!--
  help landing page
-->

<template>
  <AppBreadcrumb />
  <PageTitle id="kg-status" title="Status and QC" />
  <!-- api and service statuses -->
  <AppSection width="big" design="bare">
    <p>
      Below is a list of our service status pages, including api, api-dev, and
      others.These pages provide real-time updates on the availability and
      performance of our services. If you’re experiencing any issues, you can
      check here for:
    </p>

    <!-- main status of all checks -->
    <AppStatus v-if="isLoading" code="loading">Loading checks</AppStatus>
    <AppStatus v-if="isError" code="error">Error loading checks</AppStatus>

    <!-- individual statuses -->
    <AppGallery :cols="4">
      <AppStatus
        v-for="(uptime, index) in uptimes"
        :key="index"
        class="status"
        :code="uptime.code"
        :link="uptime.link"
        >{{ uptime.text }}</AppStatus
      >
    </AppGallery>
    <p>
      For detailed status reports, visit our
      <AppLink to="https://stats.uptimerobot.com/XPRo9s4BJ5"
        >Live Status Dashboard</AppLink
      >
    </p>

    <!-- link to uptime bot site for full details -->
    <!-- <AppButton
      to="https://stats.uptimerobot.com/XPRo9s4BJ5"
      text="More Details"
      icon="arrow-right"
    /> -->
  </AppSection>

  <AppSection width="big" design="bare">
    <p class="info">
      If you have any questions, feel free to reach out to us at :
      <a>info@monarchinitiative.org</a>
    </p></AppSection
  >
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { getUptimes } from "@/api/uptime";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import PageTitle from "@/components/PageTitle.vue";
import { useQuery } from "@/composables/use-query";

/** list of status checks to display */
const {
  query: runGetUptimes,
  data: uptimes,
  isLoading,
  isError,
} = useQuery(getUptimes, []);

onMounted(runGetUptimes);

/** clear user localstorage data */
function clearData() {
  if (
    window.confirm(
      "Are you sure you want to clear your local data? This cannot be undone.",
    )
  ) {
    window.localStorage.clear();
    window.alert(
      "Your local data has been cleared. Refresh the site for changes to take effect.",
    );
  }
}
</script>

<style lang="scss" scoped>
.status {
  justify-content: flex-start;
  padding: 0;
  gap: 10px;
}
</style>
