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

  <AppSection width="big">
    <div class="card-grid">
      <!-- Mondo Card -->
      <div class="info-card">
        <h2>Mondo Disease Ontology: Monthly Outreach Calls</h2>
        <p>
          The Mondo Outreach calls aim to bring together stakeholders and
          clinical terminology experts to discuss specific use cases and
          requirements. Our goal is to improve Mondo with a focus on our user
          needs.
        </p>
        <div class="info-box">
          <div class="info-line">
            <AppIcon icon="calendar-week" />
            <span>
              These calls are scheduled monthly. Explore details on
              <AppLink
                to="https://mondo.monarchinitiative.org/pages/workshop/#outreach"
              >
                our workshop page</AppLink
              ></span
            >
          </div>
          <div class="info-line">
            <AppIcon icon="envelope" />
            <span>
              Subscribe to the Mondo users mailing list via
              <AppLink to="https://groups.google.com/g/mondo-users">
                Google Groups
              </AppLink></span
            >
          </div>
        </div>
      </div>

      <div class="info-card">
        <h2>Monarch Seminar Series</h2>
        <p>
          A monthly forum for exploring topics central to the Monarch
          Initiative.
        </p>
        <div class="info-box">
          <div class="info-line">
            <AppIcon icon="book-open-reader" />

            <span>
              Learn more about the series in our
              <AppLink
                to="https://monarch-initiative.github.io/monarch-documentation/seminars"
              >
                seminar archive
              </AppLink>

              .</span
            >
          </div>
          <div class="info-line">
            <AppIcon icon="youtube" />
            <span>
              Browse past recordings on our
              <AppLink to="https://www.youtube.com/@monarchinitiative"
                >YouTube channel</AppLink
              >
              .</span
            >
          </div>
          <div class="info-line">
            <AppIcon icon="envelope" />
            <span>
              To participate, send an email to
              <a href="mailto:info@monarchinitiative.org"
                >info@monarchinitiative.org</a
              >
              with the subject:
              <strong>"Join the Monarch Seminar Series"</strong>.
            </span>
          </div>
        </div>
      </div>

      <!-- OBO Academy Card -->
      <div class="info-card">
        <h2>OBO Academy: Monarch Training Series</h2>
        <p>
          Training for Semantic Engineers, Ontology Curators, and Knowledge
          Scientists on basic technologies in and around the Monarch Initiative
          and Open Biological and Biomedical Ontologies (OBO).The OBO Academy
          develops self-paced tutorials in the OBOOK, hosts monthly live
          training sessions on Zoom, and maintains a YouTube channel with lesson
          recordings.
        </p>

        <div class="info-box">
          <div class="info-line">
            <AppIcon icon="graduation-cap" />
            <span>
              Learn more about the curriculum at the
              <AppLink
                to="https://oboacademy.github.io/obook/courses/monarch-obo-training/"
              >
                OBO Academy
              </AppLink>
              site.
            </span>
          </div>

          <div class="info-line">
            <AppIcon icon="youtube" />
            <span>
              Watch recorded lessons on
              <AppLink to="https://www.youtube.com/@obo-academy">
                our YouTube channel</AppLink
              >.
            </span>
          </div>

          <div class="info-line">
            <AppIcon icon="envelope" />
            <span>
              Sign up for updates via the
              <AppLink to="https://groups.google.com/g/monarch-tutorials">
                OBO Academy Google Group </AppLink
              >.
            </span>
          </div>
        </div>
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
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #000;
  transition: transform 0.2s ease;

  .app-icon {
    color: white;
    font-size: 1rem;
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
  color: #7d4cdb;
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

.info-line {
  display: flex;
  align-items: center;
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
    background: #708090; // slate gray like your screenshot
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
