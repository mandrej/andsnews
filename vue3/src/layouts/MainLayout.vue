<template>
  <q-layout view="hHh Lpr lFf">
    <q-header elevated>
      <q-toolbar class="bg-white text-black">
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />
        <q-linear-progress v-show="busy" color="secondary" class="absolute-bottom" indeterminate />

        <q-toolbar-title>
          <router-link to="/" class="text-black" style="text-decoration: none">{{ title }}</router-link>
        </q-toolbar-title>

        <vue3-autocounter
          v-if="route.name === 'list'"
          class="q-px-xs"
          :startAmount="oldCount"
          :endAmount="newCount"
          :duration="1"
          :suffix="sufixCount"
          :autoinit="true"
        />
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
import { defineComponent, defineAsyncComponent, computed, ref, watch } from "vue";
import Vue3Autocounter from 'vue3-autocounter';

const Stat = defineAsyncComponent(() =>
  import('../components/Stat.vue')
)

export default defineComponent({
  name: "MainLayout",
  components: {
    Find,
    Menu,
    Stat,
    Vue3Autocounter
  },
  setup() {
    const store = useStore();
    const busy = computed(() => store.state.app.busy)

    const leftDrawerOpen = ref(false);
    const route = useRoute();
    const counter = computed(() => store.getters["app/counter"])
    const newCount = ref(0)
    const oldCount = ref(0)
    const sufixCount = ref('')

    const dynamic = computed(() => {
      switch (route.name) {
        case 'home':
        case 'list':
          return Find
        default:
          return Stat
      }
    })

    watch(counter, (value, oldValue) => {
      newCount.value = value.count
      oldCount.value = oldValue.count || 0
      sufixCount.value = value.more ? '+' : ''
    });

    return {
      busy,
      route,
      newCount,
      oldCount,
      sufixCount,
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
