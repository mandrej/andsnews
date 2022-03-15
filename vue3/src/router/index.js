import { createRouter, createWebHistory } from "vue-router";
import routes from "./routes";
import { trackRouter } from "vue-gtag-next";

const router = createRouter({
  scrollBehavior: (to, from, savedPosition) => {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { left: 0, top: 0 };
    }
  },
  routes,
  history: createWebHistory(),
});

trackRouter(router);
export default router;
