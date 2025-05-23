<template>
  <AppBreadcrumb />

  <PageTitle id="get-involved" title="Get Involved" />

  <AppSection width="big" class="intro-section">
    <p class="intro-text">
      The Monarch Initiative is a community effort, and we welcome your
      participation!
    </p>
    <div class="social-follow">
      <div class="icons">
        <AppSocialIcon
          type="email"
          icon="envelope"
          url="https://groups.google.com/g/monarch-friends/"
        />
        <AppSocialIcon
          type="medium"
          icon="medium"
          url="https://medium.com/@MonarchInit"
        />
        <AppSocialIcon
          type="linkedin"
          icon="linkedin"
          url="https://www.linkedin.com/company/the-monarch-initiative"
        />
        <AppSocialIcon
          type="github"
          icon="github"
          url="https://github.com/monarch-initiative"
        />
        <AppSocialIcon
          type="youtube"
          icon="youtube"
          url="https://www.youtube.com/@monarchinitiative"
        />
        <AppSocialIcon
          type="bluesky"
          icon="social-bluesky"
          url="https://bsky.app/profile/monarchinitiative.bsky.social"
        />
      </div>
    </div>
  </AppSection>

  <AppSection width="big">
    <div class="card-grid">
      <PageInfoCard
        title="Mondo Disease Ontology: Monthly Outreach Calls"
        description="The Mondo Outreach calls aim to bring together stakeholders and clinical terminology experts to discuss specific use cases and requirements. Our goal is to improve Mondo with a focus on our user needs."
      >
        <div class="info-line">
          <AppIcon icon="calendar-week" />
          <span>
            These calls are scheduled monthly. Explore details on the
            <AppLink
              to="https://mondo.monarchinitiative.org/pages/workshop/#outreach"
            >
              Mondo workshop page </AppLink
            >.
          </span>
        </div>
        <div class="info-line">
          <AppIcon icon="envelope" />
          <span>
            Subscribe to the
            <AppLink to="https://groups.google.com/g/mondo-users"
              >Mondo users mailing list</AppLink
            >
            to stay up to date on Mondo and the Mondo Outreach call.
          </span>
        </div>
      </PageInfoCard>

      <PageInfoCard
        title="Monarch Seminar Series"
        description="A monthly forum where we explore topics central to the Monarch Initiative."
      >
        <div class="info-line">
          <AppIcon icon="book-open-reader" />
          <span>
            Learn more about the series, including the past and upcoming
            schedule, at our
            <AppLink
              to="https://monarch-initiative.github.io/monarch-documentation"
              >Monarch documentation site</AppLink
            >.
          </span>
        </div>
        <div class="info-line">
          <AppIcon icon="youtube" />
          <span>
            Browse session recordings on the
            <AppLink to="https://www.youtube.com/@monarchinitiative"
              >Monarch Initiative YouTube channel</AppLink
            >.
          </span>
        </div>
        <div class="info-line">
          <AppIcon icon="envelope" />
          <span>
            Sign up for Monarch Seminar Series updates via the
            <AppLink to="https://groups.google.com/g/monarch-tutorials"
              >Monarch Tutorials and Learning mailing list</AppLink
            >
            .
          </span>
        </div>
      </PageInfoCard>

      <PageInfoCard
        title="OBO Academy: Monarch Training Series"
        description="Training for Semantic Engineers, Ontology Curators, and Knowledge Scientists on basic technologies in and around the Monarch Initiative and Open Biological and Biomedical Ontologies (OBO). The OBO Academy develops self-paced tutorials in the OBOOK, hosts monthly live training sessions on Zoom, and maintains a YouTube channel with lesson recordings."
      >
        <div class="info-line">
          <AppIcon icon="graduation-cap" />
          <span>
            Learn more about the curriculum at the
            <AppLink
              to="https://oboacademy.github.io/obook/courses/monarch-obo-training/"
            >
              OBO Academy site
            </AppLink>
            .
          </span>
        </div>
        <div class="info-line">
          <AppIcon icon="youtube" />
          <span>
            Watch recorded lessons on the
            <AppLink to="https://www.youtube.com/@obo-academy">
              OBO Academy YouTube channel</AppLink
            >.
          </span>
        </div>
        <div class="info-line">
          <AppIcon icon="envelope" />
          <span>
            Sign up for OBO Academy updates via the
            <AppLink to="https://groups.google.com/g/monarch-tutorials"
              >Monarch Tutorials and Learning mailing list</AppLink
            >" .
          </span>
        </div>
      </PageInfoCard>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppSocialIcon from "@/components/AppSocialIcon.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import PageInfoCard from "./PageInfoCard.vue";
</script>

<style scoped lang="scss">
$wrap: 1000px;
.section:last-of-type {
  margin-bottom: 3em;

  @media (max-width: $wrap) {
    padding-top: 0;
  }
}
.section:first-of-type {
  gap: 1em;
}
.emoji {
  display: inline-block;
}

.intro-text {
  max-width: 80%;
  color: #333;
  font-size: 1.1rem;
  text-align: center;
}

.icons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  width: 100%;
  gap: 1rem;
}

//icons in the content
.info-line .app-icon {
  margin-right: 0.3em;
  font-size: 1.4rem;
}
.info-line .app-icon[data-icon="calendar-week"] {
  color: #007acc;
}

.info-line .app-icon[data-icon="envelope"] {
  color: #007acc;
}

.info-line .app-icon[data-icon="youtube"] {
  color: #ff0000;
}

.info-line .app-icon[data-icon="graduation-cap"] {
  color: #25547e;
}

.social-follow {
  display: flex;
  flex-direction: column;
  align-items: left;
  max-width: 60%;
  gap: 1.2rem;
  h2 {
    text-align: left;
  }
}

.info-line {
  display: flex;
  align-items: flex-start;
  gap: 0.5em;
  color: #333;
  text-align: left;
}

.social-strip {
  display: flex;
  align-items: center;

  overflow: hidden;
  border: 1px solid #ccc;
  border-radius: 4px;

  .label {
    padding: 0.5rem 1rem;
    background: #708090;
    color: white;
    font-weight: 500;
    font-size: 0.9rem;
  }

  .icon-row {
    display: flex;
    flex-grow: 1;
    align-items: center;
    padding: 0.6rem 1rem;
    gap: 1.2rem;

    .icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: #000;
      color: white;
      font-size: 1rem;
      transition: transform 0.2s ease;

      &:hover {
        transform: scale(1.1);
        background-color: #005580;
      }
    }
  }
}
</style>
