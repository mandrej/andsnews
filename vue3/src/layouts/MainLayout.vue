<template>
  <q-layout view="hHh Lpr lFf">
    <q-header elevated>
      <q-toolbar class="bg-white text-black">
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />
        <q-linear-progress v-show="busy" color="secondary" class="absolute-bottom" indeterminate />

        <q-toolbar-title>
          <router-link to="/" class="text-black" style="text-decoration: none">{{ title }}</router-link>
        </q-toolbar-title>

        <div class="q-px-xs">{{ count }}</div>
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
import { useStore } from "vuex";
import { useRoute } from "vue-router";
import { defineComponent, defineAsyncComponent, computed, ref } from "vue";

const Stat = defineAsyncComponent(() =>
  import('../components/Stat.vue')
)

export default defineComponent({
  name: "MainLayout",
  components: {
    Find,
    Menu,
    Stat
  },
  setup() {
    const store = useStore();
    const busy = computed(() => store.state.app.busy)

    const leftDrawerOpen = ref(false);
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
    const count = computed(() => {
      if (route.name === 'list') {
        return store.getters["app/count"] // 100+
      } else {
        return ''
      }
    });

    return {
      busy,
      count,
      dynamic,
      leftDrawerOpen,
      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value;
      },
      title: computed(() => route.meta.title || 'ANDрејевићи')
    };
  },
});
</script>
