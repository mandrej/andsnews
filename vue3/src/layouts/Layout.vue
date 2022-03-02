<template>
  <q-layout view="hHh Lpr lFf">
    <q-header>
      <q-toolbar class="bg-grey-2 text-black">
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="drawer = !drawer" />
        <q-toolbar-title>
          <router-link to="/" style="color: inherit; text-decoration: none">{{ title }}</router-link>
        </q-toolbar-title>
        <div v-if="route.name === 'list'" ref="countRef" class="q-px-xs"></div>
        <q-linear-progress v-show="busy" color="warning" class="absolute-bottom" indeterminate />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="drawer" class="column no-wrap" :width="320" show-if-above>
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

<script setup>
import { defineAsyncComponent, computed, ref, watch } from "vue";
import { useStore } from "vuex";
import { useRoute } from "vue-router";
import gsap from 'gsap'

import Find from "../components/Find.vue";
import Menu from "../components/Menu.vue";
const Stat = defineAsyncComponent(() =>
  import('../components/Stat.vue')
)
const store = useStore();
const route = useRoute();
const busy = computed(() => store.state.app.busy)

const drawer = ref(false);
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

const title = computed(() => route.meta.title || 'ANDрејевићи')
</script>
