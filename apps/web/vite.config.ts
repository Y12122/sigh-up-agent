import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    chunkSizeWarningLimit: 750,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("@ant-design/icons")) return "icons";
          if (id.includes("node_modules/antd") || id.includes("node_modules/@rc-component")) return "antd";
          if (id.includes("node_modules/react") || id.includes("node_modules/scheduler")) return "react";
        }
      }
    }
  },
  test: {
    environment: "jsdom",
    exclude: ["e2e/**", "node_modules/**", "dist/**"],
    setupFiles: "./src/test/setup.ts"
  }
});
