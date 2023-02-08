module.exports = {
  root: true,

  env: {
    node: true,
    "vue/setup-compiler-macros": true,
  },

  plugins: ["vuejs-accessibility"],

  extends: [
    "plugin:vue/vue3-recommended",
    "plugin:vuejs-accessibility/recommended",
    "eslint:recommended",
    "@vue/typescript/recommended",
    "@vue/prettier",
    "@vue/prettier/@typescript-eslint",
  ],

  parserOptions: {
    ecmaVersion: 2020,
  },

  /** rule overrides (KEEP THIS AS MINIMAL AS POSSIBLE) */
  rules: {
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

  /** don't lint certain files */
  ignorePatterns: [],

  /** is this needed? */
  overrides: [
    {
      files: [
        "**/tests/unit/**/*.test.ts",
        "**/tests/accessibility/**/*.test.ts",
      ],
      env: {
        jest: true,
      },
    },
  ],
};
