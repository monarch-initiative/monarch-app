<template>
  <div class="info-card">
    <h2>{{ title }}</h2>
    <p>{{ description }}</p>
    <div class="info-box">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  description: string;
}>();
</script>
<style scoped lang="scss">
.info-card {
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  h2 {
    margin-bottom: 0.75rem;
  }

  p {
    margin-bottom: 0.75rem;
  }
}

.info-box {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 1.3em;
  gap: 1.3rem;
  border-radius: 6px;
  background-color: #f4f8fb;

  p {
    margin: 0;
    color: #333;
    text-align: left;

    a {
      color: #005580;
      font-weight: 500;
      text-decoration: underline;

      &:hover {
        text-decoration: none;
      }
    }
  }
}
</style>
