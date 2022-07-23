import { boot } from "quasar/wrappers";
import VueGtag from "vue-gtag-next";
import { CONFIG } from "../helpers";

export default boot(({ app }) => {
  app.use(VueGtag, {
    isEnabled: false,
    useDebugger: process.env.DEV ? true : false,
    property: {
      id: CONFIG.analytics,
      app_name: "ANDS",
      params: {
        send_page_view: false,
      },
    },
  });
});
