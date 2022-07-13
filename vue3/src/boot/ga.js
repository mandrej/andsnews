import { boot } from "quasar/wrappers";
import VueGtag from "vue-gtag-next";
import { CONFIG } from "../helpers";

export default boot(({ app }) => {
  app.use(VueGtag, {
    property: {
      id: CONFIG.analytics,
      app_name: "ANDS",
      send_page_view: false,
    },
  });
});
