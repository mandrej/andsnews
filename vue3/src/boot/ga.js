import { boot } from "quasar/wrappers";
import VueGtag from "vue-gtag-next";
import { useGtag } from "vue-gtag-next";

export default boot(({ app }) => {
  app.use(VueGtag, {
    appName: "ANDS",
    useDebugger: process.env.DEV ? true : false,
    property: { id: process.env.GA },
  });
  const { set } = useGtag();
  set({
    cookie_flags: "max-age=7200;secure;samesite=none",
  });
});
