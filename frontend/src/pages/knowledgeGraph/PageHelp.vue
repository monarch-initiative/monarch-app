<template>
  <AppBreadcrumb /> <PageTitle id="kg-help" title="Help" />
  <AppSection width="big">
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

  <AppSection width="big">
    <p class="info">
      If you have any questions, feel free to reach out to us at :
      <AppLink to="mailto:info@monarchinitiative.org"
        >info@monarchinitiative.org</AppLink
      >
    </p>
  </AppSection>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import PageTitle from "@/components/ThePageTitle.vue";
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
