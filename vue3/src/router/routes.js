import Layout from "../layouts/Layout.vue";
import Index from "../pages/Index.vue";
import List from "../pages/List.vue";

const routes = [
  {
    path: "/",
    component: Layout,
    children: [
      { path: "", name: "home", component: Index, meta: { plain: true } },
      { path: "list", name: "list", component: List },
      {
        path: "add",
        name: "add",
        component: () => import("../pages/Add.vue"),
        meta: {
          title: "Add",
          requiresAuth: true,
        },
      },
      {
        path: "admin",
        name: "admin",
        component: () => import("../pages/Admin.vue"),
        meta: {
          title: "Administration",
          requiresAdmin: true,
        },
      },
      // Always leave this as last one,
      // but you can also remove it
      {
        path: "/:catchAll(.*)*",
        name: "error",
        component: () => import("../pages/Error.vue"),
        props: true,
        meta: { plain: true },
      },
    ],
  },
];

export default routes;
