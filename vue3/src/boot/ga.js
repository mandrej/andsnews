import { boot } from "quasar/wrappers";
import VueGtag from "vue-gtag-next";

export default boot(({ app }) => {
  app.use(VueGtag, {
    property: {
      id: process.env.VUE_APP_GA,
      app_name: "ANDS",
      send_page_view: false,
    },
  });
});
