import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import svgLoader from "vite-svg-loader";
import vue from "@vitejs/plugin-vue";

// Plugin to copy DuckDB WASM files to public directory
function duckdbWasmPlugin() {
  return {
    name: "duckdb-wasm-copy",
    buildStart() {
      // Copy DuckDB WASM files to public directory during build
      try {
        const publicDir = "public";
        const duckdbDir = join(publicDir, "duckdb");

        // Create directory if it doesn't exist
        mkdirSync(duckdbDir, { recursive: true });

        // Find the DuckDB module path
        const duckdbPath = join(
          "node_modules",
          "@duckdb",
          "duckdb-wasm",
          "dist",
        );

        // Copy WASM files
        copyFileSync(
          join(duckdbPath, "duckdb-mvp.wasm"),
          join(duckdbDir, "duckdb-mvp.wasm"),
        );
        copyFileSync(
          join(duckdbPath, "duckdb-browser-mvp.worker.js"),
          join(duckdbDir, "duckdb-browser-mvp.worker.js"),
        );

        console.log("✓ DuckDB WASM files copied to public/duckdb/");
      } catch (error) {
        console.warn(
          "Warning: Could not copy DuckDB WASM files:",
          error.message,
        );
      }
    },
  };
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), svgLoader({ svgo: false }), duckdbWasmPlugin()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "@/global/variables.scss" as *;`,
      },
    },
  },
  optimizeDeps: {
    exclude: ["@duckdb/duckdb-wasm"],
  },
});
