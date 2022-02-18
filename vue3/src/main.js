import { createApp } from "vue";
import { Quasar, Notify, Dialog } from "quasar";
import router from "./router";
import store from "./store";
import quasarIconSet from "quasar/icon-set/svg-material-icons";
// Import icon libraries
import "@quasar/extras/roboto-font/roboto-font.css";
import "@quasar/extras/material-icons/material-icons.css";
import "quasar/src/css/index.sass";
// https://vite-plugin-pwa.netlify.app/guide/auto-update.html
import { registerSW } from "virtual:pwa-register";

import App from "./App.vue";

const app = createApp(App);
const updateSW = registerSW({
  onOfflineReady() {},
});

app.use(Quasar, {
  plugins: { Notify, Dialog }, // import Quasar plugins and add here
  iconSet: quasarIconSet,
  config: {
    brand: {
      // primary: '#e46262',
      // ... or all other brand colors
    },
    // notify: {}, default set of options for Notify Quasar plugin
    // loading: {...}, // default set of options for Loading Quasar plugin
    // loadingBar: { ... }, // settings for LoadingBar Quasar plugin
    // ..and many more (check Installation card on each Quasar component/directive/plugin)
  },
});
app.use(store);
app.use(router);
// app.config.devtools = true;
// Assumes you have a <div id="app"></div> in your index.html
app.mount("#app");
