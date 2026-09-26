// Temporary dev-server config for serving on the LAN. Not committed.
//
// The app resolves `api=local` to a hard-coded http://127.0.0.1:8000, which from another
// machine means that machine's own localhost. Serving over the LAN instead leaves the
// API url relative (`/v3/api`) and proxies it here, which also sidesteps CORS.
import base from "./vite.config.mjs";

export default {
  ...base,
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    // Vite rejects a Host header it does not recognise (DNS-rebinding protection), so
    // reaching this by name rather than by IP needs the name listed.
    allowedHosts: [
      "monarch.local",
      "monarch",
      "monarch.tail6c0fa3.ts.net",
      "localhost",
      "192.168.1.225",
    ],
    proxy: {
      "/v3/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
};
