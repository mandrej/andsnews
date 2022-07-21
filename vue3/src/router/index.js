import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { trackRouter } from "vue-gtag-next";
import { CONFIG } from "../helpers";
import routes from "./routes";

const router = createRouter({
  scrollBehavior: () => ({ left: 0, top: 0 }),
  routes,
  history: createWebHistory(process.env.VUE_ROUTER_BASE),
});

router.beforeEach((to, from, next) => {
  const auth = useAuthStore();
  const user = auth.user;
  if (user && user.uid) {
    if (+new Date() - +new Date(user.lastLogin) > CONFIG.lifeSpan) {
      auth.signIn();
    }
    if (to.meta.requiresAuth && !user.isAuthorized) {
      next({ name: "error", params: { code: 401 } });
    } else if (to.meta.requiresAdmin && !user.isAdmin) {
      next({ name: "error", params: { code: 401 } });
    } else {
      next();
    }
  }
});
trackRouter(router);

export default router;
