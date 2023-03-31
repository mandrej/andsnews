import Layout from "../layouts/Layout.vue";
import Index from "../pages/Index.vue";
import List from "../pages/List.vue";
import { CONFIG } from "../helpers";

const routes = [
  {
    path: "/",
    component: Layout,
    children: [
      {
        path: "",
        name: "home",
        component: Index,
        meta: { title: CONFIG.title, plain: true },
      },
      {
        path: "list",
        name: "list",
        component: List,
        meta: { title: CONFIG.title },
      },
      {
        path: "add",
        name: "add",
        component: () => import("../pages/Add.vue"),
        meta: { title: "Add", requiresAuth: true },
      },
      {
        path: "admin",
        name: "admin",
        component: () => import("../pages/Admin.vue"),
        meta: { title: "Administration", requiresAdmin: true },
      },
      {
        path: "401",
        name: "401",
        component: () => import("../pages/Error.vue"),
        props: { code: 401 },
        meta: { title: "Error 401", plain: true },
      },
      // Always leave this as last one,
      // but you can also remove it
      {
        path: "/:pathMatch(.*)*",
        name: "404",
        component: () => import("../pages/Error.vue"),
        props: { code: 404 },
        meta: { title: "Error 404", plain: true },
      },
    ],
  },
];

export default routes;
