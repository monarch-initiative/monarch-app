<template>
  <AppBreadcrumb />

  <PageTitle id="get-involved" title="Get Involved" />

  <AppSection width="big" class="intro-section">
    <p class="intro-text">
      The Monarch Initiative is a community effort, and we welcome your
      participation!
    </p>
  </AppSection>

  <AppSection width="big">
    <div class="card-grid">
      <!-- Mondo Card -->
      <div class="info-card">
        <h2>
          <AppLink to="https://mondo.monarchinitiative.org">
            Mondo Disease Ontology (Mondo)
          </AppLink>
        </h2>
        <p>
          Mondo aims to harmonize disease definitions across the world. The name
          comes from the Latin word ‘mundus’ and means ‘for the world.’
        </p>
        <div class="info-box">
          <div class="info-line">
            <span class="emoji">📌</span>
            <span>
              The Mondo Outreach calls aim to bring together stakeholders and
              clinical terminology experts to discuss specific use cases and
              requirements. Our goal is to improve Mondo with a focus on our
              user needs.</span
            >
          </div>
          <div class="info-line">
            <span class="emoji">📅</span>
            <span>
              These calls are scheduled monthly. You can find more information
              about the calls
              <AppLink
                to="https://mondo.monarchinitiative.org/pages/workshop/#outreach"
                >here</AppLink
              ></span
            >
          </div>
          <div class="info-line">
            <span class="emoji">✉️</span>
            <span
              >Join the Mondo users mailing list
              <AppLink to="https://groups.google.com/g/mondo-users">
                here
              </AppLink></span
            >
          </div>
        </div>
      </div>

      <!-- OBO Academy Card -->
      <div class="info-card">
        <h2>
          <AppLink
            to="https://oboacademy.github.io/obook/courses/monarch-obo-training/"
          >
            OBO Academy: Monarch Training Series
          </AppLink>
        </h2>
        <p>
          Training for Semantic Engineers, Ontology Curators, and Knowledge
          Scientists on basic technologies in and around the Monarch Initiative
          and Open Biological and Biomedical Ontologies (OBO).
        </p>

        <div class="info-box">
          <div class="info-line">
            <span class="emoji">🎓</span>
            <span>
              The OBO Academy develops self-paced tutorials in the OBOOK, hosts
              fortnightly live training sessions on Zoom, and maintains a
              YouTube channel with lesson recordings.
            </span>
          </div>

          <div class="info-line">
            <span class="emoji">📺</span>
            <span>
              YouTube channel:
              <AppLink to="https://www.youtube.com/@obo-academy"
                >https://www.youtube.com/@obo-academy</AppLink
              >
            </span>
          </div>

          <div class="info-line">
            <span class="emoji">✉️</span>
            <span>
              Join the OBO Academy mailing list
              <AppLink to="https://groups.google.com/g/monarch-tutorials">
                here </AppLink
              >.
            </span>
          </div>
        </div>
      </div>
    </div>
  </AppSection>

  <AppSection width="big">
    <div class="social-follow">
      <h2>Connect with us</h2>
      <div class="icons">
        <span class="social-icon email"
          ><AppLink to="https://groups.google.com/g/monarch-friends/"
            ><AppIcon icon="envelope" /></AppLink
        ></span>
        <span class="social-icon medium"
          ><AppLink to="https://medium.com/@MonarchInit"
            ><AppIcon icon="medium" /></AppLink
        ></span>
        <span class="social-icon linkedin"
          ><AppLink to="https://www.linkedin.com/company/the-monarch-initiative"
            ><AppIcon icon="linkedin" /></AppLink
        ></span>
        <span class="social-icon github"
          ><AppLink to="https://github.com/monarch-initiative"
            ><AppIcon icon="github" /></AppLink
        ></span>
        <span class="social-icon youtube"
          ><AppLink to="https://www.youtube.com/@monarchinitiative"
            ><AppIcon icon="youtube" /></AppLink
        ></span>
        <span class="social-icon bluesky"
          ><AppLink to="https://bsky.app/profile/monarchinitiative.bsky.social"
            ><AppIcon icon="bluesky" /></AppLink
        ></span>
      </div>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import PageTitle from "@/components/ThePageTitle.vue";
</script>
<style scoped lang="scss">
$wrap: 1000px;
.section:last-of-type {
  margin-bottom: 3em;
}
.section:first-of-type {
  padding-botton: 0;
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

.info-card {
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  h2 {
    margin-bottom: 0.75rem;
    color: #005580;
    font-size: 1.2rem;
  }

  p {
    margin-bottom: 0.75rem;
  }
}

.icons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
}

.social-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #000;
  transition: transform 0.2s ease;

  .app-icon {
    color: white;
    font-size: 1.4rem;
  }

  &:hover {
    transform: scale(1.1);
  }
}

// Platform-specific colors
.social-icon.email {
  background-color: #007acc;
}

.social-icon.medium {
  background-color: #000000;
}

.social-icon.github {
  background-color: #333333;
}

.social-icon.linkedin {
  background-color: #0a66c2;
}

.social-icon.youtube {
  background-color: #ff0000;
}

.social-icon.bluesky {
  background-color: #1185fe;
}

.social-follow {
  display: flex;
  flex-direction: column;
  align-items: left;
  gap: 1.2rem;
  h2 {
    text-align: left;
  }
}

.info-box {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 1em;
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

.info-line {
  display: flex;
  align-items: flex-start;
  gap: 0.5em;
  color: #333;
  text-align: left;
}
</style>
