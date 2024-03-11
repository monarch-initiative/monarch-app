import { fileURLToPath } from "node:url";
import { mergeConfig } from "vite";
import { defineConfig } from "vitest/config";
import viteConfig from "./vite.config.mjs";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      setupFiles: "./unit/setup.ts",
      environment: "jsdom",
      include: ["./unit/**/*.test.ts"],
      root: fileURLToPath(new URL("./", import.meta.url)),
    },
  }),
);
