import { createRouter, createWebHistory } from "vue-router";
import routes from "./routes";
import { useAuthStore } from "../store/auth";
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

router.beforeEach((to, from, next) => {
  // ✅ This will work because the router starts its navigation after
  // the router is installed and pinia will be installed too
  const auth = useAuthStore();
  const user = auth.user;
  if (to.meta.requiresAuth && !user.isAuthorized) {
    next({ name: "error", params: { code: 401 } });
  } else if (to.meta.requiresAdmin && !user.isAdmin) {
    next({ name: "error", params: { code: 401 } });
  } else {
    next();
  }
});

trackRouter(router);
export default router;
