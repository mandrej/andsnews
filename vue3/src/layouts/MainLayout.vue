<template>
  <q-layout view="hHh Lpr lFf">
    <q-header elevated>
      <q-toolbar class="bg-white text-black">
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          <router-link to="/" class="text-black" style="text-decoration: none">{{ title }}</router-link>
        </q-toolbar-title>

        <div class="q-px-xs">{{ version }}</div>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" class="column no-wrap" :width="320" show-if-above bordered>
      <keep-alive>
        <component :is="dynamic"></component>
      </keep-alive>
      <q-space />
      <Menu />
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import Find from "../components/Find.vue";
import Menu from "../components/Menu.vue";
import Stat from "../components/Stat.vue";
import { useRoute } from "vue-router";

import { defineComponent, computed, reactive, ref } from "vue";

export default defineComponent({
  name: "MainLayout",
  components: {
    Find,
    Menu,
    Stat
  },

  setup() {
    const leftDrawerOpen = ref(false);
    const version = computed(() => {
      const ver = import.meta.env.VUE_APP_VERSION.match(/.{1,4}/g).join(".");
      return "© 2007 - " + ver;
    });
    const route = useRoute();
    const dynamic = computed(() => {
      switch (route.name) {
        case 'home':
        case 'list':
          return Find
        default:
          return Stat
      }
    })

    return {
      dynamic,
      version,
      leftDrawerOpen,
      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value;
      },
      title: computed(() => route.meta.title || 'ANDрејевићи')
    };
  },
});
</script>
