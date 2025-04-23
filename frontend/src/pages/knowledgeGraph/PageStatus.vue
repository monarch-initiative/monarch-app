<!--
  help landing page
-->
<template>
  <AppBreadcrumb /> <PageTitle id="kg-status" title="Status and QC" />
  <!-- api and service statuses -->
  <AppSection width="big">
    <p class="content">
      Below is a list of our service status pages, including api, api-dev, and
      others. These pages provide real-time updates on the availability and
      performance of our services. If you’re experiencing any issues, you can
      check here.
    </p>
    <!-- main status of all checks -->
    <AppStatus v-if="isLoading" code="loading">Loading checks</AppStatus>
    <AppStatus v-if="isError" code="error">Error loading checks</AppStatus>
    <!-- individual statuses -->
    <AppGallery :cols="cols">
      <AppStatus
        v-for="(uptime, index) in uptimes"
        :key="index"
        class="status"
        :code="uptime.code"
        :link="uptime.link"
      >
        {{ uptime.text }}</AppStatus
      >
    </AppGallery>
    <p>
      For detailed status reports, visit our
      <AppLink to="https://stats.uptimerobot.com/XPRo9s4BJ5" :no-icon="true"
        >Live Status Dashboard</AppLink
      >
    </p>

    <p class="content">
      Additionally, for data validation and quality control insights, visit our
      <AppLink to="https://qc.monarchinitiative.org/"
        >Quality Control (QC) Dashboard</AppLink
      >. This dashboard provides reports on data consistency, error tracking,
      and validation checks to ensure high-quality biomedical data integration
      within our platform.
    </p>
  </AppSection>

  <AppSection width="big">
    <AppHeading>Local Data</AppHeading>
    <p>
      Clear all of your
      <AppLink to="/terms#local-data">locally-saved data</AppLink>, such as your
      recent searches and feedback form drafts.
    </p>
    <AppButton text="Clear Local Data" icon="floppy-disk" @click="clearData" />
  </AppSection>

  <AppSection width="big">
    <p class="content">
      If you have any questions, feel free to reach out to us at :
      <AppLink to="mailto:info@monarchinitiative.org"
        >info@monarchinitiative.org
      </AppLink>
    </p>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { getUptimes } from "@/api/uptime";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import { useQuery } from "@/composables/use-query";

/** list of status checks to display */
const {
  query: runGetUptimes,
  data: uptimes,
  isLoading,
  isError,
} = useQuery(getUptimes, []);

onMounted(runGetUptimes);

const screenWidth = ref(window.innerWidth);

const updateScreenWidth = () => {
  screenWidth.value = window.innerWidth;
};

// Listen for window resize
onMounted(() => {
  window.addEventListener("resize", updateScreenWidth);
});

onUnmounted(() => {
  window.removeEventListener("resize", updateScreenWidth);
});

// Dynamically adjust `cols`
const cols = computed(() => (screenWidth.value <= 1300 ? 2 : 4));

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

.content {
  text-align: left;
}

@media (max-width: 600px) {
  section.center[data-v-d078f057] {
    align-items: unset;
  }
}
</style>
