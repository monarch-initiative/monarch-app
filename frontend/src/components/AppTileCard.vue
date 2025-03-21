<template>
  <div class="tile">
    <div class="tile-text">
      <h3>{{ title }}</h3>
      <p class="tile-content">{{ content }}</p>
    </div>

    <AppButton to="" text="Explore" class="app-button" />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  title: string;
  content: string;
  buttonText?: string;
}>();

console.log("Button Text:", props.buttonText);
</script>

<style lang="scss" scoped>
$wrap: 1000px;

.tile {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  width: 380px;
  padding: 1.1em;
  gap: 10px;
  background-color: #a6ecf257;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  @media (max-width: $wrap) {
    width: 100%;
  }
}

.tile-text {
  display: flex;
  flex-direction: column;
  gap: 1.6em;
  text-align: left;
}

.tile-content {
  font-size: 0.9rem;
}

.tile-button {
  align-self: center;
}

.app-button {
  min-width: unset !important;
}
h3 {
  padding: unset;
}
</style>
