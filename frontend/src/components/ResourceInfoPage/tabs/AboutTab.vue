<template>
  <AppSection v-if="item?.about" width="big">
    <div class="formatted-about" v-html="formattedAbout"></div>


    
      <AppLink v-if="externalLink" :to="externalLink.href" :no-icon="true" class="learn-more">
        Learn more about  {{ externalLink.text }}   here.
      </AppLink>
    


    <div v-if="item.visual_explainer" class="visual-explainer">
      <div class="video" v-if="
        explainerParts.videoUrl && /youtu\.?be/.test(explainerParts.videoUrl)
      ">
        <h2>Watch: What Is {{ item?.title }} and Why It Matters</h2>
        <iframe :src="embedYouTubeUrl(explainerParts.videoUrl)" frameborder="0" allow="autoplay; picture-in-picture"
          allowfullscreen :title="`Visual explainer video for ${item.title}`"></iframe>
      </div>

      <p v-if="explainerParts.description">{{ explainerParts.description }}</p>

      <figure v-if="explainerParts.imageId">
        <img :src="`/icons/${explainerParts.imageId}.png`" :alt="`Visual explainer image for ${item.title}`" />
      </figure>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AppLink from "@/components/AppLink.vue";
import AppSection from "@/components/AppSection.vue";
import { embedYouTubeUrl } from "../helpers/youtube";

const props = defineProps<{
  item: Record<string, any>;
  externalLink: { href: string; text: string } | null;
  explainerParts: {
    videoUrl?: string;
    imageId?: string;
    description?: string;
  };
}>();

//Formatting about section
const formattedAbout = computed(() => {
  const text = props.item.about ?? "";
  const lines = text.split("\n");
  const html: string[] = [];
  let inList = false;

  for (let raw of lines) {
    const line = raw.trim();
    if (line.startsWith("- ")) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${line.slice(2)}</li>`);
    } else {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
      if (line) {
        html.push(`<p>${line}</p>`);
      }
    }
  }

  if (inList) {
    html.push("</ul>");
  }

  return html.join("");
});

</script>

<style scoped lang="scss">
$wrap: 1000px;

.visual-explainer {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  gap: 2rem;

  h2 {
    text-align: left;
  }

  .video {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    gap: 1.5rem;

    iframe {
      aspect-ratio: 16 / 9;
      width: 70%;
      border-radius: 8px;

      @media (max-width: $wrap) {
        width: 100%;
      }
    }
  }

  img {
    align-self: center;
    width: 70%;
  }
}

.formatted-about ::v-deep p {
  margin-bottom: 0.5em;
}

.formatted-about ul {
  padding-left: 1.5em;
  list-style-position: inside;
}

.formatted-about ul li {
  margin-bottom: 0.5em;
}

.learn-more {
  width: 100%;
  text-align: left;
  text-decoration: none;

}
</style>
