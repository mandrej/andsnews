import { createApp } from "vue";
import { Quasar, Notify, Dialog } from "quasar";
import router from "./router";
import store from "./store";
import quasarIconSet from "quasar/icon-set/svg-material-icons";
// Import icon libraries
import "@quasar/extras/roboto-font/roboto-font.css";
import "@quasar/extras/material-icons/material-icons.css";
// Import Quasar css
import "quasar/src/css/index.sass";

import App from "./App.vue";

const app = createApp(App);

app.use(Quasar, {
  plugins: { Notify, Dialog }, // import Quasar plugins and add here
  iconSet: quasarIconSet,
  config: {
    brand: {
      // primary: '#e46262',
      // ... or all other brand colors
    },
    notify: {
      position: "bottom-left",
    }, // default set of options for Notify Quasar plugin
    // loading: {...}, // default set of options for Loading Quasar plugin
    // loadingBar: { ... }, // settings for LoadingBar Quasar plugin
    // ..and many more (check Installation card on each Quasar component/directive/plugin)
  },
});
app.use(store);
app.use(router);
// app.config.devtools = true
// Assumes you have a <div id="app"></div> in your index.html
app.mount("#app");
