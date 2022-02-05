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
    }),
    quasar({
      sassVariables: "src/quasar-variables.sass",
    }),
    VitePWA({
      includeAssets: [
        "favicon.ico",
        "robots.txt",
        "assets/icons/pwa-192x192.png",
        "assets/icons/pwa-512x512.png",
      ],
      manifest: {
        name: "Andрејевићи",
        short_name: "ANDS",
        start_url: ".",
        display: "standalone",
        background_color: "#222",
        theme_color: "#fff",
        icons: [
          {
            src: "assets/icons/pwa-192x192.png",
            sizes: "192x192",
            type: "image/png",
          },
          {
            src: "assets/icons/pwa-512x512.png",
            sizes: "512x512",
            type: "image/png",
          },
          {
            src: "assets/icons/pwa-512x512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any maskable",
          },
        ],
        gcm_sender_id: "103953800507",
      },
    }),
  ],
  envPrefix: "VUE_",
});
