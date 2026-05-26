import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    coverage: { provider: "v8", thresholds: { lines: 85 } },
  },
  resolve: { alias: { "@": "/Users/salah/Projects/orch-ai-agents/hw2/frontend" } },
});
