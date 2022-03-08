import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { quasar, transformAssetUrls } from "@quasar/vite-plugin";
import { VitePWA } from "vite-plugin-pwa";

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:6060/api",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
  plugins: [
    vue({
      template: { transformAssetUrls },
      // https://vuejs.org/guide/extras/reactivity-transform.html#explicit-opt-in
      reactivityTransform: true,
    }),
    quasar({
      sassVariables: "src/quasar-variables.sass",
    }),
    VitePWA({
      strategies: "injectManifest",
      registerType: "autoUpdate",
    }),
  ],
  envPrefix: "VUE_",
});
