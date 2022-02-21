<template>
  <q-layout view="hHh Lpr lFf">
    <q-header elevated>
      <q-toolbar class="bg-white text-black">
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />
        <q-linear-progress v-show="busy" color="secondary" class="absolute-bottom" indeterminate />

        <q-toolbar-title>
          <router-link to="/" class="text-black" style="text-decoration: none">{{ title }}</router-link>
        </q-toolbar-title>

        <div v-if="route.name === 'list'" ref="countRef" class="q-px-xs"></div>
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
import { defineComponent, defineAsyncComponent, computed, ref, watch } from "vue";
import { useStore } from "vuex";
import { useRoute } from "vue-router";
import Find from "../components/Find.vue";
import Menu from "../components/Menu.vue";
import gsap from 'gsap'

const Stat = defineAsyncComponent(() =>
  import('../components/Stat.vue')
)

export default defineComponent({
  name: "MainLayout",
  components: {
    Find,
    Menu,
    Stat,
  },
  setup() {
    const store = useStore();
    const busy = computed(() => store.state.app.busy)

    const leftDrawerOpen = ref(false);
    const route = useRoute();
    const counter = computed(() => store.getters["app/counter"])
    const countRef = ref(null)

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
      const div = countRef.value
      if (!div) return
      const obj = { number: oldValue.count };
      const sufix = value.more ? '+' : ''
      gsap.to(obj, {
        duration: 1,
        number: value.count,
        ease: "power1.in",
        onUpdate() {
          div.innerText = obj.number.toFixed(0) + sufix;
        }
      });

    });

    return {
      busy,
      route,
      countRef,
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
