/* eslint-env node */
require("@rushstack/eslint-patch/modern-module-resolution");

module.exports = {
  root: true,
  extends: [
    "plugin:vue/vue3-recommended",
    "plugin:vuejs-accessibility/recommended",
    "eslint:recommended",
    "@vue/eslint-config-typescript",
    "@vue/eslint-config-prettier/skip-formatting",
  ],
  parserOptions: {
    ecmaVersion: "latest",
  },

  /** rule overrides (KEEP THIS AS MINIMAL AS POSSIBLE) */
  rules: {
    "prettier/prettier": "warn",

    /**
     * count v-tooltip (which adds an accessible aria-label attribute) as
     * accessible
     */
    "vuejs-accessibility/anchor-has-content": [
      "error",
      { accessibleDirectives: ["tooltip"] },
    ],
    /**
     * allow nesting a control in a label without a for attribute (perfectly
     * fine practice)
     */
    "vuejs-accessibility/label-has-for": [
      "error",
      {
        controlComponents: ["AppInput"],
        required: { some: ["nesting", "id"] },
        allowChildren: true,
      },
    ],
    /**
     * allow v-html. we are only using this from very controlled sources, so
     * little risk of XSS.
     */
    "vue/no-v-html": ["off"],
    "vue/no-v-text-v-html-on-component": ["off"],
  },
};
