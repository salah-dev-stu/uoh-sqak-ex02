import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react({ jsxRuntime: "automatic" })],
  esbuild: { jsx: "automatic", jsxImportSource: "react" },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./vitest.setup.ts"],
    coverage: { provider: "v8", thresholds: { lines: 85 } },
  },
  resolve: { alias: { "@": "/Users/salah/Projects/orch-ai-agents/hw2/frontend" } },
});
