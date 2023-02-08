<!--
  a card for a blog post, with image/icon to left, and lines of text content
  to right
-->

<template>
  <div class="post">
    <div class="image" :data-image="!!image">
      <img :src="image" alt="" />
    </div>
    <AppFlex h-align="left" direction="col" gap="small" class="text">
      <span class="date">{{
        date.toLocaleDateString(undefined, {
          day: "numeric",
          month: "long",
          year: "numeric",
        })
      }}</span>
      <AppLink class="link" :to="link">
        {{ title }}
      </AppLink>
      <p class="description truncate-2">
        {{ description }}
      </p>
    </AppFlex>
  </div>
</template>

<script setup lang="ts">
interface Props {
  /** src of image */
  image?: string;
  /** post details */
  date: Date;
  link: string;
  title: string;
  description: string;
}

defineProps<Props>();
</script>

<style lang="scss" scoped>
.post {
  display: flex;
  width: 100%;
  gap: 20px;
}

@media (max-width: 400px) {
  .post {
    align-items: center;
    flex-direction: column;
  }
}

.image {
  width: 100px;
  height: 100px;
  flex-shrink: 0;
  overflow: hidden;

  &[data-image="true"] {
    box-shadow: $shadow;
  }

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  svg {
    width: 100%;
    height: 100%;
    color: $off-black;
  }
}

.text {
  text-align: left;
}

.link {
  line-height: $spacing;
}

.description {
  font-size: 0.9rem;
  line-height: $spacing;
}

.date {
  color: $gray;
  font-size: 0.9rem;
}
</style>
