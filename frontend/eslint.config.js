import url from "url";
import eslintPluginPrettierRecommended from "eslint-plugin-prettier/recommended";
import pluginVue from "eslint-plugin-vue";
import { FlatCompat } from "@eslint/eslintrc";
import js from "@eslint/js";
import prettierConfig from "@vue/eslint-config-prettier";
import vueTsEslintConfig from "@vue/eslint-config-typescript";

const __dirname = url.fileURLToPath(new URL(".", import.meta.url));
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  // allConfig: js.configs.all,
});

export default [
  /** Extend recommended configs */
  ...compat.extends(
    "plugin:vue/vue3-recommended",
    "plugin:vuejs-accessibility/recommended",
    "eslint:recommended",
    "@vue/eslint-config-prettier/skip-formatting",
  ),
  ...pluginVue.configs["flat/recommended"],
  ...vueTsEslintConfig(),
  eslintPluginPrettierRecommended,
  prettierConfig,
  {
    ignores: [
      "node_modules",
      "dist",
      "mockServiceWorker.js",
      "src/api/model.ts",
    ],
  },
  /** Configuration */
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
      "@typescript-eslint/no-empty-object-type": ["warn"],
      "@typescript-eslint/no-unused-expressions": ["off"],
      "@typescript-eslint/no-unused-vars": ["off"],
      "max-len": ["error", { code: 120 }],
      "no-constant-binary-expression": ["off"],
      "prefer-const": 0,
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
];
