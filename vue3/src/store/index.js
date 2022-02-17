// import { def } from "@vue/shared";
import { createStore, createLogger } from "vuex";
import createPersistedState from "vuex-persistedstate";
import app from "./modules/app";
import auth from "./modules/auth";

const debug = import.meta.env.NODE_ENV !== "production";
const persisted = createPersistedState({
  key: "ands",
  paths: [
    "auth.user",
    "auth.fcm_token",
    "app.dark",
    "app.find",
    "app.last",
    "app.bucket",
    "app.values",
    "app.uploaded",
    "app.objects",
    "app.pages",
    "app.next",
  ],
});
const plugins = [persisted];
if (debug) {
  plugins.push(createLogger({}));
}

const store = createStore({
  modules: {
    app,
    auth,
  },
  strict: debug,
  plugins,
});

export default store;
