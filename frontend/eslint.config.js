import url from "url";
import eslintPluginPrettierRecommended from "eslint-plugin-prettier/recommended";
import pluginVue from "eslint-plugin-vue";
import { FlatCompat } from "@eslint/eslintrc";
import js from "@eslint/js";
import prettierConfig from "@vue/eslint-config-prettier";
import {
  defineConfigWithVueTs,
  vueTsConfigs,
} from "@vue/eslint-config-typescript";

const __dirname = url.fileURLToPath(new URL(".", import.meta.url));
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
});

export default defineConfigWithVueTs(
  compat.extends(
    "plugin:vuejs-accessibility/recommended",
    "eslint:recommended",
  ),
  eslintPluginPrettierRecommended,
  pluginVue.configs["flat/recommended"],
  prettierConfig,
  vueTsConfigs.recommended,
  {
    ignores: [
      "node_modules",
      "dist",
      "public/mockServiceWorker.js",
      "src/api/model.ts",
    ],
  },
  /** Additional Configuration */
  {
    languageOptions: {
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "script",
      },
    },
    files: [
      "**/*.js",
      "**/*.cjs",
      "**/*.mjs",
      "**/*.ts",
      "**/*.tsx",
      "**/*.vue",
    ],
    /** Override rules */
    rules: {
      "max-len": ["error", { code: 120 }],
      "no-constant-binary-expression": ["off"],
      "prefer-const": "off",
      "@typescript-eslint/no-empty-object-type": ["warn"],
      "@typescript-eslint/no-explicit-any": ["warn"],
      "@typescript-eslint/no-unused-expressions": ["off"],
      "@typescript-eslint/no-unused-vars": ["off"],
      "prettier/prettier": ["warn", {}, { usePrettierrc: true }],
      "vue/attribute-hyphenation": [
        "warn",
        "always",
        { ignore: ["selectedFilters"] },
      ],
      "vue/no-v-html": ["off"],
      "vue/no-v-text-v-html-on-component": ["off"],
      "vuejs-accessibility/anchor-has-content": [
        "error",
        {
          accessibleDirectives: ["tooltip"],
        },
      ],
      "vuejs-accessibility/label-has-for": [
        "error",
        {
          required: {
            some: ["nesting", "id"],
          },
          allowChildren: true,
        },
      ],
      "vuejs-accessibility/mouse-events-have-key-events": ["off"],
    },
  },
);
