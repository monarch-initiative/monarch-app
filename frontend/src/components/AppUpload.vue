<!--
  upload button
-->

<template>
  <AppButton
    v-tooltip="'Choose or drag & drop a file'"
    class="button"
    text="Upload"
    icon="upload"
    :data-drag="drag"
    @click="onClick"
    @dragenter="drag = true"
    @dragleave="drag = false"
    @dragover.prevent
    @drop.prevent.stop="onDrop"
  />

  <input
    ref="input"
    aria-label="invisible input"
    type="file"
    accept="text/plain"
    :style="{ display: 'none' }"
    @change="onChange"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";

type Emits = {
  (event: "upload", content: string, filename: string): void;
}

const emit = defineEmits<Emits>();

/** dragging state */
const drag = ref(false);
/** input element */
const input = ref<HTMLInputElement>();

/** upload file */
async function upload(target: HTMLInputElement | DataTransfer | null) {
  /** get file name and contents from event */
  const file = (target?.files || [])[0];
  const content = (await file.text()) || "";
  const filename = file?.name || "";

  /** signal upload to parent */
  emit("upload", content, filename);

  /** reset file input */
  if (content && input.value) input.value.value = "";
}

/** on file input change */
function onChange(event: Event) {
  upload(event.target as HTMLInputElement);
}

/** on button click, click hidden file input */
function onClick() {
  input.value?.click();
}

/** on button file drop */
function onDrop(event: DragEvent) {
  drag.value = false;
  upload(event.dataTransfer);
}
</script>

<style lang="scss" scoped>
.button[data-drag="true"] {
  outline: dashed 2px $black;
  box-shadow: none !important;
}

/** prevent button children from messing with drag state */
.button > :deep(*) {
  pointer-events: none;
}
</style>
