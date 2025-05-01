<template>
  <footer class="footer">
    <div class="container">
      <div class="logo-column">
        <ResourceIcon class="footer-logo" />
        <p>© Monarch Initiative 2025. BSD-3</p>
      </div>

      <div
        v-for="(column, index) in navigationMenus"
        :key="index"
        class="footer-column"
      >
        <h4>{{ column.label }}</h4>
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
  padding: 30px max(20px, (100% - 1200px) / 2);
  background: #d3e6eb;
  font-size: 0.9rem;

  .container {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    max-width: 1000px;

    gap: 4rem;
  }

  .logo-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-weight: 600;
    text-align: center;
    > svg {
      margin: 0;
    }
  }

  .footer-column {
    display: flex;
    flex-direction: column;
    align-items: center;

    h4 {
      margin: unset;
      font-weight: bold;
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
</style>
