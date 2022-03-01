import Front from "../layouts/Front.vue";
import Layout from "../layouts/Layout.vue";
import Index from "../pages/Index.vue";
import List from "../pages/List.vue";
import store from "../store";

const routes = [
  {
    path: "/",
    component: Front,
    children: [{ path: "", name: "home", component: Index }],
  },
  {
    path: "/list",
    component: Layout,
    children: [{ path: "", name: "list", component: List }],
  },
  {
    path: "/add",
    component: Layout,
    meta: { title: "Add" },
    children: [
      {
        path: "",
        name: "add",
        component: () => import("../pages/Add.vue"),
      },
    ],
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
    path: "/admin",
    component: Layout,
    meta: { title: "Administration" },
    children: [
      {
        path: "",
        name: "admin",
        component: () => import("../pages/Admin.vue"),
      },
    ],
    beforeEnter: (to, from, next) => {
      const user = store.state.auth.user;
      if (user.isAdmin) {
        next();
      } else {
        next({ name: "401" });
      }
    },
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: "/:catchAll(.*)*",
    component: Front,
    children: [
      {
        path: "",
        name: "404",
        component: () => import("../pages/Error404.vue"),
      },
    ],
  },
  {
    path: "/:catchAll(.*)*",
    component: Front,
    children: [
      {
        path: "",
        name: "401",
        component: () => import("../pages/Error401.vue"),
      },
    ],
  },
];

export default routes;
