<!--
  help landing page
-->

<template>
  <!-- main links -->
  <AppSection>
    <AppHeading>Help</AppHeading>
    <p>
      Request a feature, report a bug, or chat with us about anything
      Monarch-related.
    </p>
    <AppFlex gap="big">
      <AppTile
        icon="comment"
        title="Feedback Form"
        subtitle="Right here, no account required, one-way"
        to="/feedback"
      />
      <AppTile
        icon="comments"
        title="Help Desk"
        subtitle="On GitHub, requires account, two-way"
        to="https://github.com/monarch-initiative/helpdesk"
      />
    </AppFlex>
  </AppSection>

  <!-- api and service statuses -->
  <AppSection>
    <AppHeading>Status</AppHeading>

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
    <!-- link to uptime bot site for full details -->
    <AppButton
      to="https://stats.uptimerobot.com/XPRo9s4BJ5"
      text="More Details"
      icon="arrow-right"
    />
  </AppSection>

  <AppSection>
    <AppHeading>Local Data</AppHeading>
    <p>
      Clear all of your locally-saved data, such as your recent searches and
      feedback form drafts.
      <AppLink to="/terms#local-data">Learn more.</AppLink>
    </p>
    <AppButton text="Clear Local Data" icon="floppy-disk" @click="clearData" />
  </AppSection>

  <!-- last resort contact methods -->
  <AppSection>
    <p>
      If you still need help, or for general inquires, you can
      <AppLink to="mailto:info@monarchinitiative.org">email us</AppLink>.
    </p>
  </AppSection>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { getUptimes } from "@/api/uptime";
import { useQuery } from "@/util/composables";

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
      "Your local data has been cleared. Restart the app for changes to take effect.",
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
