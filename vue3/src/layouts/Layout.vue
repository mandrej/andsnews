<template>
  <q-layout v-if="route.meta.plain" view="hHh lpR fFf">
    <q-page-container>
      <q-page class="row">
        <div class="col-xs-12 col-sm-6 last" :style="styling"></div>
        <div class="col-xs-12 col-sm-6" style="max-height: 180px;">
          <div class="bg-grey-2 q-pa-md">
            <div class="text-h4">{{ title }} personal photo album</div>
            <div class="text-h6">{{ bucketInfo.count }} photos since 2007 and counting</div>
          </div>
          <router-view />
          <div class="absolute-bottom q-pa-md text-right">{{ version }}</div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
  <q-layout v-else view="hHh Lpr lFf">
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
import { defineAsyncComponent, computed, watch, ref } from "vue";
import { useStore } from "vuex";
import { useRoute } from "vue-router";
import { fullsized, smallsized } from "../helpers";
import gsap from 'gsap'

import Find from "../components/Find.vue";
import Menu from "../components/Menu.vue";
const Stat = defineAsyncComponent(() =>
  import('../components/Stat.vue')
)
const store = useStore();
const route = useRoute();

const last = computed(() => store.state.app.last);
const title = computed(() => route.meta.title || 'ANDрејевићи')
const bucketInfo = computed(() => store.state.app.bucket)

const styling = computed(() => {
  const low = smallsized + last.value.filename;
  const high = fullsized + last.value.filename;
  return "background-image: url(" + high + "), url(" + low + ")";
});
const version = computed(() => {
  const ver = import.meta.env.VUE_APP_VERSION.match(/.{1,4}/g).join(".");
  return "© 2007 - " + ver;
});

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
    duration: 0.5,
    number: value.count,
    onUpdate() {
      div.innerText = obj.number.toFixed(0) + sufix;
    }
  });
});
</script>

<style scoped>
.last {
  background-size: cover;
  background-position: center;
  transition: background-image 0.5s ease-in-out;
}
</style>
