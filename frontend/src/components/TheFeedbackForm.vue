<!--
  feedback form higher-order component
-->

<template>
  <!-- add heading -->
  <AppHeading v-if="modal" :level="1">Feedback Form</AppHeading>

  <!-- overview info -->
  <p>
    Request a feature, report a bug, or chat with us about anything
    Monarch-related.
  </p>

  <!-- form -->
  <form class="form" @submit.prevent="onSubmit">
    <!-- fields for user to fill out -->
    <div class="fields">
      <AppTextbox
        v-model.trim="name"
        title="Name"
        description="So we can address you"
        placeholder="Jane Smith"
      />
      <AppTextbox
        v-model.trim="email"
        title="Email"
        description="So we can follow up with you"
        placeholder="jane.smith@gmail.com"
        type="email"
      />
      <AppTextbox
        v-model.trim="github"
        title="GitHub username"
        description="So we can tag you"
        placeholder="@janesmith"
      />
      <div class="feedback">
        <AppTextbox
          v-model="feedback"
          title="Feedback"
          description="Please give us as many details as possible!"
          placeholder=""
          :required="true"
          :multi="true"
        />
      </div>
    </div>

    <!-- auto-submitted details -->
    <div class="details">
      <template v-for="(value, key) in details" :key="key">
        <span>{{ key }}</span>
        <span v-html="value.replaceAll(/([^A-Za-z0-9])/g, '<wbr />$1')"></span>
      </template>
    </div>

    <!-- finish up -->
    <p>
      Submitting this form starts a <strong>public</strong> discussion on our
      <AppLink to="https://github.com/monarch-initiative/helpdesk"
        >help desk</AppLink
      >
      on GitHub with <strong>all of the information above</strong>. You'll get a
      link to the discussion once it's created.
    </p>

    <!-- status -->
    <AppStatus v-if="isLoading" code="loading">Submitting feedback</AppStatus>
    <AppStatus v-if="isError" code="error">Error submitting feedback</AppStatus>
    <AppStatus v-if="isSuccess" code="success">
      <AppLink v-if="link" :to="link"
        >View your submitted feedback here.</AppLink
      >
    </AppStatus>

    <!-- submit button -->
    <AppButton v-else text="Submit" icon="paper-plane" type="submit" />
  </form>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { truncate } from "lodash";
import parser from "ua-parser-js";
import { useLocalStorage } from "@vueuse/core";
import { postFeedback } from "@/api/feedback";
import AppTextbox from "@/components/AppTextbox.vue";
import { useQuery } from "@/util/composables";
import { collapse } from "@/util/string";

/** route info */
const route = useRoute();

type Props = {
  /** whether form is inside a modal */
  modal?: boolean;
};

withDefaults(defineProps<Props>(), { modal: false });

/** user's name */
const name = useLocalStorage("feedback-form-name", "");
/** user's email */
const email = useLocalStorage("feedback-form-email", "");
/** user's github name */
const github = useLocalStorage("feedback-form-github", "");
/** user's freeform feedback */
const feedback = useLocalStorage("feedback-form-feedback", "");

/** list of automatic details to record */
const details = computed(() => {
  /** get browser/device/os/etc details from ua parser library */
  const { browser, device, os, engine, cpu } = parser();

  /** filter and join strings together */
  const concat = (...array: (string | undefined)[]) =>
    array.filter((e) => e && e !== "()").join(" ");

  /** make map of desired properties in desired stringified format */
  return {
    Page: route.fullPath,
    Browser: concat(browser.name, browser.version),
    Device: concat(device.vendor, device.model, device.type),
    OS: concat(os.name, os.version, cpu.architecture),
    Engine: concat(engine.name, engine.version),
  };
});

/** when form submitted */
async function onSubmit() {
  /**
   * only proceed if submitted through button, not "implicitly" (enter press).
   * https://stackoverflow.com/questions/895171/prevent-users-from-submitting-a-form-by-hitting-enter
   */
  if ((document.activeElement as Element).matches("button[type='submit']"))
    await submitFeedback();
}

/** post feedback to backend */
const {
  query: submitFeedback,
  data: link,
  isLoading,
  isError,
  isSuccess,
} = useQuery(async function () {
  /** make issue title (unclear what char limit is?) */
  const title = [
    "Feedback form",
    truncate(name.value, { length: 20 }),
    truncate(collapse(feedback.value), { length: 60 }),
  ].join(" - ");

  /** make issue body markdown */
  const body = [
    "**Name**",
    name.value,
    "",
    "**Email**",
    email.value,
    "",
    "**GitHub Username**",
    github.value,

    "",
    "**Details**",
    ...Object.entries(details.value).map(([key, value]) => `${key}: ${value}`),
    "",
    "",
    feedback.value,
  ].join("\n");

  /** post feedback and get link of created issue */
  const link = await postFeedback(title, body);

  resetForm();

  return link;
}, "");

/** clear form data from storage after successful submit */
function resetForm() {
  name.value = null;
  email.value = null;
  github.value = null;
  feedback.value = null;
}
</script>

<style lang="scss" scoped>
.heading {
  font-size: 1.3rem;
  text-align: center;
  font-weight: 600;
}

.form {
  display: contents;
  margin-top: 40px;
}

.fields {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 40px;
  width: 100%;
}

.feedback {
  grid-column: 1 / span 3;
}

@media (max-width: 700px) {
  .fields {
    grid-template-columns: 1fr;
  }

  .feedback {
    grid-column: unset;
  }
}

.details {
  display: grid;
  grid-template-columns: 100px 1fr 100px 1fr;
  gap: 10px;
  justify-items: flex-start;
  width: 100%;
  color: $dark-gray;
  text-align: left;

  & > *:nth-child(odd) {
    font-weight: 600;
  }

  @media (max-width: 800px) {
    grid-template-columns: 100px 1fr;
  }
}
</style>
