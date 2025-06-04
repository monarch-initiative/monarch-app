<template>
  <AppBreadcrumb />
  <ThePageTitle id="contact-us" title="Contact Us" />

  <AppSection width="big">
    <div class="contact-content">
      <!--Information -->
      <div class="left">
        <p class="question">
          Have any questions or need assistance?<br />
          Feel free to reach out to us at:
        </p>
        <a href="mailto:info@monarchinitiative.org" class="email">
          info@monarchinitiative.org
        </a>

        <div class="social">
          <p>Follow us on:</p>
          <div class="icons">
            <AppLink
              v-tooltip="'Subscribe'"
              to="https://groups.google.com/g/monarch-friends/"
              class="social-icon"
            >
              <AppIcon icon="envelope" />
            </AppLink>
            <AppLink
              v-tooltip="'Medium'"
              to="https://medium.com/@MonarchInit"
              class="social-icon"
            >
              <AppIcon icon="medium" />
            </AppLink>
            <AppLink
              v-tooltip="'GitHub'"
              to="https://github.com/monarch-initiative"
              class="social-icon"
            >
              <AppIcon icon="github" />
            </AppLink>
            <AppLink
              v-tooltip="'LinkedIn'"
              to="https://www.linkedin.com/company/the-monarch-initiative"
              class="social-icon"
            >
              <AppIcon icon="linkedin" />
            </AppLink>

            <AppLink
              v-tooltip="'YouTube'"
              to="https://www.youtube.com/@monarchinitiative"
              class="social-icon"
            >
              <AppIcon icon="youtube" />
            </AppLink>

            <AppLink
              v-tooltip="'blusky'"
              to="https://bsky.app/profile/monarchinitiative.bsky.social"
              class="social-icon"
            >
              <AppIcon icon="social-bluesky" />
            </AppLink>
          </div>
        </div>
      </div>

      <!-- form -->
      <form class="form" @submit.prevent="runPostFeedback">
        <AppTextbox
          v-model.trim="name"
          placeholder="Name"
          :required="true"
          @keydown="preventImplicit"
        />
        <AppTextbox
          v-model.trim="email"
          placeholder="Email"
          type="email"
          :required="true"
          @keydown="preventImplicit"
        />
        <AppTextbox
          v-model.trim="github"
          placeholder="GitHub username (optional)"
          @keydown="preventImplicit"
        />
        <AppTextbox
          v-model="message"
          placeholder="Message"
          :required="true"
          :multi="true"
        />
        <!-- status -->
        <AppStatus v-if="isLoading" code="loading">
          Sending your message...
        </AppStatus>
        <AppStatus v-if="isError" code="error">
          Oops! Something went wrong. Please try again later.</AppStatus
        >
        <AppStatus v-if="isSuccess" code="success">
          <template v-if="link">
            <AppLink :to="link">View your message here.</AppLink>
          </template>
          <template v-else>
            Thank you! Your message has been submitted successfully.
          </template>
        </AppStatus>

        <!-- submit button -->
        <AppButton
          v-else
          text="Submit"
          icon="paper-plane"
          type="submit"
          design="tile"
        />
      </form>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { truncate } from "lodash";
import parser from "ua-parser-js";
import { useLocalStorage } from "@vueuse/core";
import { postFeedback } from "@/api/feedback";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppButton from "@/components/AppButton.vue";
import AppTextbox from "@/components/AppTextbox.vue";
import ThePageTitle from "@/components/ThePageTitle.vue";
import { useQuery } from "@/composables/use-query";
import { collapse } from "@/util/string";

/** route info */
const route = useRoute();

/** user's name */
const name = useLocalStorage("contact-form-name", "");
/** user's email */
const email = useLocalStorage("contact-form-email", "");
/** user's message */
const message = useLocalStorage("contact-form-message", "");
/** user's github name */
const github = useLocalStorage("contact-form-github", "");
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

/** https://stackoverflow.com/questions/895171/prevent-users-from-submitting-a-form-by-hitting-enter */
async function preventImplicit(event: KeyboardEvent) {
  if (event.key === "Enter") event.preventDefault();
}

/** post feedback to backend */
const {
  query: runPostFeedback,
  data: link,
  isLoading,
  isError,
  isSuccess,
} = useQuery(async function () {
  /** make issue title (unclear what char limit is?) */
  const title = [
    "Contact form",
    truncate(name.value, { length: 20 }),
    truncate(collapse(message.value), { length: 60 }),
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
    message.value,
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
  message.value = null;
}
</script>

<style scoped lang="scss">
$wrap: 768px;
.contact-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  width: 100%;
  margin-top: 2rem;
  padding: 0 1rem;
  gap: 1.2rem;

  @media (max-width: $wrap) {
    flex-direction: column;
    align-content: center;
    align-items: stretch;
    justify-content: unset;
  }
}

.left {
  flex: 1;
  min-width: 280px;
  max-width: 400px;
  text-align: left;
  @media (max-width: $wrap) {
    width: 100%;
  }
}

.question {
  font-weight: 400;
  font-size: 1.1rem;
}

.email {
  display: inline-block;

  color: #2b7bb9;
  font-size: 1.1rem;
  text-decoration: none;
}

.social {
  margin-top: 1rem;
}

.icons {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
  @media (max-width: $wrap) {
    max-width: 100%;
  }
}

.form {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 280px;
  max-width: 400px;
  gap: 1rem;
  @media (max-width: $wrap) {
    width: 100%;
  }
}

.form input,
.form textarea {
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form textarea {
  min-height: 120px;
  resize: vertical;
}

.form button {
  align-self: flex-end;
  padding: 0.7rem 2rem;
  border: none;
  border-radius: 4px;
  background-color: #555;
  color: white;
  font-size: 1rem;
  cursor: pointer;
}

.form button:hover {
  background-color: #333;
}

.social-icon {
  margin-right: 0.5rem;
  font-size: 1.6rem;

  .app-icon {
    vertical-align: middle;

    &:hover {
      transform: scale(1.1);
      opacity: 0.8;
      transition: all 0.2s ease;
    }
  }

  .app-icon[data-icon="github"] {
    color: #181717;
  }

  .app-icon[data-icon="linkedin"] {
    color: #0a66c2;
  }

  .app-icon[data-icon="youtube"] {
    color: #ff0000;
  }

  .app-icon[data-icon="envelope"] {
    color: #007acc;
  }
}
</style>
