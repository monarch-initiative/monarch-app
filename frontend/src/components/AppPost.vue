<!--
  a card for a blog post, with image/icon to left, and lines of text content
  to right
-->

<template>
  <div class="post">
    <div v-if="image" class="image">
      <img :src="image" alt="" />
    </div>
    <AppFlex align-h="left" direction="col" gap="small" class="text">
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
type Props = {
  /** src of image */
  image?: string;
  /** post details */
  date: Date;
  link: string;
  title: string;
  description: string;
};

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
    flex-direction: column;
    align-items: center;
  }
}

.image {
  flex-shrink: 0;
  width: 100px;
  height: 100px;
  overflow: hidden;
  box-shadow: $shadow;

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
