<template>
  <AppBreadcrumb />
  <PageTitle id="kg-help" title="Help" />
  <AppSection width="big" design="bare">
    <p>
      We welcome all questions, requests, and feedback! Request a feature,
      report a bug, or chat with us about anything Monarch-related. We will
      connect you with someone who can help.
    </p>
    <AppFlex gap="big">
      <AppTile
        icon="question"
        title="How to Use"
        subtitle="Still confused?"
        to="/how-to"
      />
      <AppTile
        icon="comment"
        title="Feedback Form"
        subtitle="Right here, no account required"
        to="/feedback"
      />
      <AppTile
        icon="comments"
        title="Help Desk"
        subtitle="On GitHub, requires account"
        to="https://github.com/monarch-initiative/helpdesk"
      />
    </AppFlex>
  </AppSection>

  <AppSection width="big" design="bare">
    <AppHeading>Local Data</AppHeading>
    <p>
      Clear all of your
      <AppLink to="/terms#local-data">locally-saved data</AppLink>, such as your
      recent searches and feedback form drafts.
    </p>
    <AppButton text="Clear Local Data" icon="floppy-disk" @click="clearData" />
  </AppSection>

  <AppSection width="big" design="bare">
    <p class="info">
      If you have any questions, feel free to reach out to us at :
      <AppLink to="mailto:info@monarchinitiative.org"
        >info@monarchinitiative.org</AppLink
      >
    </p></AppSection
  >
</template>

<script setup lang="ts">
import { onMounted } from "vue";
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
.section.big {
  @media (max-width: 1000px) {
    padding: 1em;
  }
}
</style>
