<template>
  <AppSection v-if="item.citation" width="big">
    <div class="citation-container">
      <pre ref="citationText" class="citation-box"
        >{{ formatApaCitation(item.citation) }}
      </pre>

      <AppButton text="Copy Citation" class="copy-btn" @click="copyCitation" />
      <span v-if="copied" class="copied-msg">Copied!</span>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { formatApaCitation } from "../helpers/citation";

defineProps<{
  item: Record<string, any>;
}>();

const copied = ref(false);
const citationText = ref<HTMLElement | null>(null);

function copyCitation() {
  if (citationText.value) {
    const text = citationText.value.innerText;
    navigator.clipboard.writeText(text).then(() => {
      copied.value = true;
      setTimeout(() => (copied.value = false), 2000);
    });
  }
}
</script>
<style scoped lang="scss">
.citation-container {
  padding: 1rem;
  border-radius: 6px;
  background: #f9f9f9;
  font-size: 0.95em;
}

.citation-box {
  padding: 1rem;
  border-radius: 8px;
  background: #f7f7f7;
  font-family: monospace;
  white-space: pre-wrap;
}

.copy-btn {
  margin-top: 0.5rem;
}

.copied-msg {
  margin-left: 1rem;
  color: $black;
}
</style>
