<!--
  report a problem with one dismech record: one-click problems for the kind of
  record plus an optional comment, posted to the help desk with the record, its
  evidence, and its mechanism chain
-->

<template>
  <AppButton
    v-tooltip="'Dismech is AI-assisted curation. Tell us if this is wrong.'"
    class="report"
    text="Report a problem"
    icon="flag"
    icon-position="left"
    design="small"
    color="secondary"
    @click="open = true"
  />
  <AppModal v-model="open" label="Report a problem with a Dismech record">
    <!-- not a heading, so the table of contents leaves it out -->
    <div class="title">Report a problem</div>
    <div class="record">
      <div class="muted">
        <AppIcon icon="robot" class="ai" /> Dismech
        {{ KIND_LABELS[record.kind].toLowerCase() }} record
      </div>
      <strong>{{ record.claim }}</strong>
      <div v-for="[key, value] in record.fields" :key="key" class="field">
        <span class="muted">{{ key }}</span> {{ value }}
      </div>
    </div>

    <form class="form" @submit.prevent="submit">
      <div class="reasons" role="group" aria-label="What's wrong?">
        <button
          v-for="reason in reasonsFor(record)"
          :key="reason"
          type="button"
          :class="['reason', { selected: reasons.includes(reason) }]"
          :aria-pressed="reasons.includes(reason)"
          @click="toggle(reason)"
        >
          {{ reason }}
        </button>
      </div>
      <AppTextbox
        v-model="comment"
        title="Comment (optional)"
        description="What's wrong, and what should it say? Citations help."
        :multi="true"
      />
      <details class="contact">
        <summary>Contact details (optional)</summary>
        <div class="fields">
          <AppTextbox v-model.trim="name" title="Name" />
          <AppTextbox v-model.trim="email" title="Email" type="email" />
          <AppTextbox v-model.trim="github" title="GitHub username" />
        </div>
      </details>
      <details class="preview">
        <summary>
          Sent with your report: this record,
          {{ plural(record.evidence.length, "evidence quote")
          }}<template v-if="record.chain.length">, its mechanism chain</template
          >, and this page's address
        </summary>
        <pre>{{ issue.body }}</pre>
      </details>
      <p class="muted">
        Submitting starts a <strong>public</strong> discussion on our
        <AppLink to="https://github.com/monarch-initiative/helpdesk"
          >help desk</AppLink
        >
        on GitHub with everything above.
      </p>
      <AppStatus v-if="isLoading" code="loading">Submitting</AppStatus>
      <AppStatus v-else-if="isError" code="error"
        >Error submitting feedback</AppStatus
      >
      <AppStatus v-if="isSuccess" code="success">
        Thank you.
        <AppLink v-if="link" :to="link">View your report.</AppLink>
      </AppStatus>
      <AppButton
        v-else
        text="Submit"
        icon="paper-plane"
        type="submit"
        :disabled="!reasons.length && !comment.trim()"
      />
    </form>
  </AppModal>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useLocalStorage } from "@vueuse/core";
import { postFeedback } from "@/api/feedback";
import AppModal from "@/components/AppModal.vue";
import AppTextbox from "@/components/AppTextbox.vue";
import { useQuery } from "@/composables/use-query";
import { plural } from "@/util/dismech";
import type { DismechFeedbackRecord } from "@/util/dismech-feedback";
import {
  feedbackIssue,
  KIND_LABELS,
  reasonsFor,
} from "@/util/dismech-feedback";
import { feedbackDetails } from "@/util/feedback";

type Props = {
  record: DismechFeedbackRecord;
};

const props = defineProps<Props>();

const open = ref(false);
const reasons = ref<string[]>([]);
const comment = ref("");
/** contact details, shared with the page feedback form */
const name = useLocalStorage("feedback-form-name", "");
const email = useLocalStorage("feedback-form-email", "");
const github = useLocalStorage("feedback-form-github", "");

const toggle = (reason: string) =>
  (reasons.value = reasons.value.includes(reason)
    ? reasons.value.filter((r) => r !== reason)
    : [...reasons.value, reason]);

const issue = computed(() =>
  feedbackIssue(
    props.record,
    reasons.value,
    comment.value.trim(),
    { name: name.value, email: email.value, github: github.value },
    feedbackDetails(window.location.href),
  ),
);

const {
  query: submit,
  data: link,
  isLoading,
  isError,
  isSuccess,
} = useQuery(async () => {
  const link = await postFeedback(issue.value.title, issue.value.body);
  reasons.value = [];
  comment.value = "";
  return link;
}, "");

/** a fresh form each time it opens after a submit */
watch(open, (value) => {
  if (value && isSuccess.value) link.value = "";
});
</script>

<style lang="scss" scoped>
.report {
  align-self: flex-start;
}

.title {
  font-weight: 600;
  font-size: 1.3rem;
}

.record {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 10px 15px;
  gap: 4px;
  border-left: solid 3px $theme;
  background: $off-white;
  text-align: left;
}

.form {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  gap: 20px;
}

.reasons {
  display: flex;
  flex-wrap: wrap;
  width: 100%;
  gap: 8px;
}

.reason {
  padding: 4px 12px;
  border: solid 1px $theme;
  border-radius: 999px;
  background: $white;
  color: $theme;
  cursor: pointer;

  &.selected {
    background: $theme;
    color: $white;
  }
}

.contact,
.preview {
  width: 100%;
  text-align: left;

  summary {
    cursor: pointer;
  }
}

.fields {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  margin-top: 10px;
  gap: 20px;
}

.preview pre {
  max-height: 300px;
  overflow: auto;
  font-size: 0.8em;
  white-space: pre-wrap;
}

.muted {
  color: $dark-gray;
  font-size: 0.9em;
}

.ai {
  color: $theme;
}
</style>
