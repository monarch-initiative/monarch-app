<template>
  <footer class="footer">
    <div class="container">
      <!-- Logo & Social -->
      <div class="left-column">
        <div class="logo-column">
          <ResourceIcon class="footer-logo" />
          <p>© Monarch Initiative</p>
          <p>2025. BSD-3</p>
        </div>
        <div class="social">
          <p>Follow us on</p>
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
            <AppLink
              v-tooltip="'blusky'"
              to="https://bsky.app/profile/monarchinitiative.bsky.social"
              class="social-icon"
            >
              <AppIcon icon="social-bluesky" />
            </AppLink>
          </div>
        </div>
      </div>

      <div
        v-for="(column, index) in navigationMenus"
        :key="index"
        class="right-column"
      >
        <p>{{ column.label }}</p>
        <ul>
          <li v-for="subItem in column.subItems" :key="subItem.key">
            <AppLink
              v-tooltip="subItem.tooltip"
              :to="subItem.to"
              class="app-link"
            >
              {{ subItem.label }}
              <span v-if="subItem.icon" class="icon">
                <AppIcon icon="arrow-up-right-from-square" />
              </span>
            </AppLink>
          </li>
        </ul>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import ResourceIcon from "@/assets/icons/resource-monarch-black.svg";
import AppLink from "@/components/AppLink.vue";
import navigationMenus from "@/data/navigationMenu.json";
</script>

<style scoped lang="scss">
.footer {
  display: flex;
  justify-content: center;
  padding: 30px 0;
  background: #d3e6eb;
  font-size: 0.9rem;

  .container {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    gap: 1rem;
  }

  .logo-column {
    display: flex;
    flex-direction: column;
    align-items: center;

    text-align: center;
    > svg {
      margin: 0;
    }
  }

  .right-column {
    display: flex;
    flex: 1;
    flex-direction: column;
    align-items: flex-start;
    min-width: 120px;
    text-align: left;

    p {
      padding-left: 0.7em;
      font-weight: bold;
      text-align: left;
      word-break: keep-all;
    }

    ul {
      margin: 0;
      padding: 0;
      list-style: none;

      li {
        margin-bottom: 0.5rem;

        a {
          color: inherit;
          text-decoration: none;
          transition: color 0.2s;

          &:hover {
            color: $theme;
          }
        }
      }
    }
  }
}

.footer-logo {
  width: 40px;
  height: auto;
  margin-bottom: 1rem;
}
.app-link {
  font-weight: 500;
}
.social-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;

  h4 {
    margin: 0;
    font-weight: bold;
  }
}
.left-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2em;
}

.social-icon {
  margin-right: 0.5rem;
  font-size: 1.4rem;

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

  .app-icon[data-icon="bluesky"] {
    color: #1185fe;
  }
}

.social {
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>
