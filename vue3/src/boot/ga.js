import { boot } from "quasar/wrappers";
import VueGtag from "vue-gtag-next";
import { useGtag } from "vue-gtag-next";
import { CONFIG } from "../helpers";

export default boot(({ app }) => {
  app.use(VueGtag, {
    useDebugger: process.env.DEV ? true : false,
    property: {
      id: CONFIG.analytics,
      app_name: "ANDS",
    },
  });
  const { set } = useGtag();
  set({ cookie_flags: "max-age=7200;secure;samesite=none" });
});
