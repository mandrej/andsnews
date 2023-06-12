import Plain from "../layouts/Plain.vue";
import Layout from "../layouts/Layout.vue";
import Find from "../components/Find.vue";
import Stat from "../components/Stat.vue";
import Index from "../pages/Index.vue";
import List from "../pages/List.vue";
import { CONFIG } from "../helpers";

const routes = [
  {
    path: "/",
    name: "home",
    component: Index,
    meta: { title: CONFIG.title, layout: Plain },
  },
  {
    path: "/list",
    name: "list",
    component: List,
    meta: { title: CONFIG.title, layout: Layout, sidebar: Find },
  },
  {
    path: "/add",
    name: "add",
    component: () => import("../pages/Add.vue"),
    meta: { title: "Add", requiresAuth: true, layout: Layout, sidebar: Stat },
  },
  {
    path: "/admin",
    name: "admin",
    component: () => import("../pages/Admin.vue"),
    meta: {
      title: "Administration",
      requiresAdmin: true,
      layout: Layout,
      sidebar: Stat,
    },
  },
  {
    path: "/401",
    name: "401",
    component: () => import("../pages/Error.vue"),
    props: { code: 401 },
    meta: { title: "Error 401", layout: Plain },
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: "/:pathMatch(.*)*",
    name: "404",
    component: () => import("../pages/Error.vue"),
    props: { code: 404 },
    meta: { title: "Error 404", layout: Plain },
  },
];

export default routes;
