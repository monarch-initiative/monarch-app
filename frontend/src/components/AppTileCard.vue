<template>
  <div class="tile">
    <div class="tile-text">
      <h3>{{ title }}</h3>
      <p class="tile-content">{{ content }}</p>
    </div>

    <AppButton v-if="buttonText" to="" text="Explore" design="tile" />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  content: string;
  buttonText?: string;
}>();
</script>

<style lang="scss" scoped>
$wrap: 1100px;

.tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 580px;
  min-height: 157px;
  padding: 1.5em;
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

h3 {
  padding: unset;
}
</style>
