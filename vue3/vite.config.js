import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { quasar, transformAssetUrls } from "@quasar/vite-plugin";
import { VitePWA } from "vite-plugin-pwa";

// https://vitejs.dev/config/
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          gsap: ["gsap"],
          quasar: ["quasar"],
          swiper: ["swiper"],
          gtag: ["vue-gtag-next"],
        },
      },
    },
  },
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
      manifest: {
        start_url: ".",
        name: "And\u0440\u0435\u0458\u0435\u0432\u0438\u045b\u0438",
        short_name: "ANDS",
        display: "standalone",
        background_color: "#222",
        theme_color: "#fff",
        icons: [
          {
            src: "icons/ands-144x144.png",
            sizes: "144x144",
            type: "image/png",
          },
          {
            src: "icons/ands-192x192.png",
            sizes: "192x192",
            type: "image/png",
          },
          {
            src: "icons/ands-512x512.png",
            sizes: "512x512",
            type: "image/png",
          },
          {
            src: "icons/ands-60x60.png",
            sizes: "60x60",
            type: "image/png",
          },
          {
            src: "icons/ands-76x76.png",
            sizes: "76x76",
            type: "image/png",
          },
          {
            src: "icons/ands-120x120.png",
            sizes: "120x120",
            type: "image/png",
          },
          {
            src: "icons/ands-152x152.png",
            sizes: "152x152",
            type: "image/png",
          },
          {
            src: "icons/ands-180x180.png",
            sizes: "180x180",
            type: "image/png",
          },
          {
            src: "icons/aperture.svg",
            type: "image/svg+xml",
            purpose: "any maskable",
          },
        ],
        gcm_sender_id: "103953800507",
      },
    }),
  ],
  envPrefix: "VUE_",
});
