import Layout from "../layouts/Layout.vue";
import Index from "../pages/Index.vue";
import List from "../pages/List.vue";
import store from "../store";

const routes = [
  {
    path: "/",
    component: Layout,
    children: [
      { path: "", name: "home", component: Index },
      { path: "list", name: "list", component: List },
      {
        path: "add",
        name: "add",
        component: () => import("../pages/Add.vue"),
        meta: {
          title: "Add",
        },
        beforeEnter: (to, from, next) => {
          const user = store.state.auth.user;
          if (user.isAuthorized) {
            next();
          } else {
            next({ name: "401" });
          }
        },
      },
      {
        path: "admin",
        name: "admin",
        component: () => import("../pages/Admin.vue"),
        meta: {
          title: "Administration",
        },
        beforeEnter: (to, from, next) => {
          const user = store.state.auth.user;
          if (user.isAdmin) {
            next();
          } else {
            next({ name: "401" });
          }
        },
      },
    ],
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: "/:catchAll(.*)*",
    name: "404",
    component: () => import("../pages/Error404.vue"),
  },
  {
    path: "/:catchAll(.*)*",
    name: "401",
    component: () => import("../pages/Error401.vue"),
  },
];

export default routes;
