<template>
  <AppBreadcrumb />
  <ThePageTitle id="contact-us" title="Contact Us" />

  <AppSection width="big" design="bare">
    <div class="contact-content">
      <!--Information -->
      <div class="left">
        <p class="question">
          Have any questions or need assistance?<br />
          Feel free to reach out to us at:
        </p>
        <a href="mailto:info@monarchinitiative.org" class="email">
          info@monarchinitiative.org
        </a>

        <div class="social">
          <p>Follow us on:</p>
          <div class="icons">
            <AppLink
              v-tooltip="'Subscribe'"
              to="https://groups.google.com/g/monarch-friends/"
              class="social-icon"
            >
              <AppIcon icon="envelope" />
            </AppLink>
            <AppLink
              v-tooltip="'Medium'"
              to="https://medium.com/@MonarchInit"
              class="social-icon"
            >
              <AppIcon icon="medium" />
            </AppLink>
            <AppLink
              v-tooltip="'GitHub'"
              to="https://github.com/monarch-initiative"
              class="social-icon"
            >
              <AppIcon icon="github" />
            </AppLink>
            <AppLink
              v-tooltip="'LinkedIn'"
              to="https://www.linkedin.com/company/the-monarch-initiative"
              class="social-icon"
            >
              <AppIcon icon="linkedin" />
            </AppLink>

            <AppLink
              v-tooltip="'YouTube'"
              to="https://www.youtube.com/@monarchinitiative"
              class="social-icon"
            >
              <AppIcon icon="youtube" />
            </AppLink>
          </div>
        </div>
      </div>

      <!-- form -->
      <form
        class="form"
        action="https://formsubmit.co/1e225962d9acdf7ca6770483d79d43f2"
        method="POST"
      >
        <input type="hidden" name="_next" value="/thank-you" />

        <!-- honeypot to trap bots -->
        <input
          type="text"
          name="_honey"
          style="display: none"
          tabindex="-1"
          autocomplete="off"
        />
        <!-- Hidden settings -->
        <input type="hidden" name="_captcha" value="false" />
        <input
          type="hidden"
          name="_subject"
          value="New message from Contact Form"
        />
        <input type="hidden" name="_template" value="box" />

        <!-- Form fields -->
        <input type="text" name="name" placeholder="Your name" required />
        <input type="email" name="email" placeholder="Your email" required />
        <textarea name="message" placeholder="Your message..." required />
        <button type="submit">Send</button>
      </form>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import ThePageTitle from "@/components/ThePageTitle.vue";
</script>

<style scoped lang="scss">
$wrap: 768px;
.contact-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  width: 100%;
  margin-top: 2rem;
  padding: 0 1rem;
  gap: 1.2rem;
  @media (max-width: $wrap) {
    flex-direction: column;
    align-content: center;
    align-items: stretch;
    justify-content: unset;
  }
}

.left {
  flex: 1;
  min-width: 280px;
  max-width: 400px;
  text-align: left;
  @media (max-width: $wrap) {
    width: 100%;
  }
}

.question {
  font-weight: 400;
  font-size: 1.1rem;
}

.email {
  display: inline-block;

  color: #2b7bb9;
  font-size: 1.1rem;
  text-decoration: none;
}

.social {
  margin-top: 1rem;
}

.icons {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
  @media (max-width: $wrap) {
    max-width: 100%;
  }
}

.form {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 280px;
  max-width: 400px;
  gap: 1rem;
  @media (max-width: $wrap) {
    width: 100%;
  }
}

.form input,
.form textarea {
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form textarea {
  min-height: 120px;
  resize: vertical;
}

.form button {
  align-self: flex-end;
  padding: 0.7rem 2rem;
  border: none;
  border-radius: 4px;
  background-color: #555;
  color: white;
  font-size: 1rem;
  cursor: pointer;
}

.form button:hover {
  background-color: #333;
}

.social-icon {
  margin-right: 0.5rem;
  font-size: 1.6rem;

  .app-icon {
    vertical-align: middle;

    &:hover {
      transform: scale(1.1);
      opacity: 0.8;
      transition: all 0.2s ease;
    }
  }

  .app-icon[data-icon="github"] {
    color: #181717;
  }

  .app-icon[data-icon="linkedin"] {
    color: #0a66c2;
  }

  .app-icon[data-icon="youtube"] {
    color: #ff0000;
  }

  .app-icon[data-icon="envelope"] {
    color: #007acc;
  }
}
</style>
