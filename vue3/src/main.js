import { createApp } from "vue";
import { Quasar, Notify, Dialog } from "quasar";
import router from "./router";
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
// Import icon libraries
import quasarIconSet from "quasar/icon-set/svg-material-icons";
import "@quasar/extras/roboto-font/roboto-font.css";
import "@quasar/extras/material-icons/material-icons.css";
import "quasar/src/css/index.sass";
// https://vite-plugin-pwa.netlify.app/guide/auto-update.html
import { registerSW } from "virtual:pwa-register";

import App from "./App.vue";
import VueGtag from "vue-gtag-next";

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);
// eslint-disable-next-line no-unused-vars
const updateSW = registerSW({
  onOfflineReady() {},
});

app.use(Quasar, {
  plugins: { Notify, Dialog }, // import Quasar plugins and add here
  iconSet: quasarIconSet,
});
app.use(VueGtag, {
  property: {
    id: import.meta.env.VUE_APP_GA,
    app_name: "ANDS",
    send_page_view: false,
  },
});
app.use(pinia);
app.use(router);
// app.config.devtools = true;
app.mount("#app");
