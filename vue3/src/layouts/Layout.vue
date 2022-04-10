<template>
  <q-layout v-if="route.meta.plain" view="hHh lpR fFf">
    <q-page-container>
      <q-page class="row">
        <q-responsive
          :ratio="1.75"
          class="col-xs-12 col-sm-6 last"
          :style="styling"
        />
        <!-- <div
          style="
            position: absolute;
            top: 0;
            left: 0;
            width: 192px;
            height: 192px;
            background-image: url('icons/icon-192x192.png');
            filter: drop-shadow(0 0.2rem 0.25rem rgba(0, 0, 0, 0.2));
          "
        ></div> -->
        <div class="col-xs-12 col-sm-6">
          <div class="text-black q-pa-md header">
            <div class="text-h4">
              {{ title }}
              <br />
              <span class="text-body1"
                >{{ bucketInfo.count }} photos since 2007 and counting</span
              >
            </div>
          </div>
          <router-view />
          <div class="absolute-bottom q-pa-md text-right">{{ version }}</div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
  <q-layout v-else view="hHh Lpr lFf">
    <q-header class="header fixed-top">
      <q-toolbar class="text-black">
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="drawer = !drawer"
        />
        <q-toolbar-title>
          <router-link to="/" style="color: inherit; text-decoration: none">{{
            title
          }}</router-link>
        </q-toolbar-title>
        <div v-if="route.name === 'list'" ref="countRef" class="q-px-xs" />
        <q-linear-progress
          v-show="busy"
          color="warning"
          class="absolute-bottom"
          indeterminate
        />
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="drawer"
      class="column no-wrap"
      :width="320"
      show-if-above
    >
      <keep-alive>
        <component :is="dynamic" />
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
import { useAppStore } from "../stores/app";
import { useRoute } from "vue-router";
import { fullsized, smallsized } from "../helpers";
import gsap from "gsap";

import Find from "../components/Find.vue";
import Menu from "../components/Menu.vue";

const Stat = defineAsyncComponent(() => import("../components/Stat.vue"));

const app = useAppStore();
const route = useRoute();

const last = computed(() => app.last);
const title = computed(() => route.meta.title || "ANDрејевићи");
const bucketInfo = computed(() => app.bucket);
const busy = computed(() => app.busy);
const drawer = ref(false);

const counter = computed(() => app.counter);
const countRef = ref(null);

const styling = computed(() => {
  const low = smallsized + last.value;
  const high = fullsized + last.value;
  return "background-image: url(" + high + "), url(" + low + ")";
});
const version = computed(() => {
  const ver = process.env.VUE_APP_VERSION.match(/.{1,4}/g).join(".");
  return "© 2007 - " + ver;
});

const dynamic = computed(() => {
  switch (route.name) {
    case "home":
    case "list":
      return Find;
    default:
      return Stat;
  }
});

watch(counter, (value, oldValue) => {
  const div = countRef.value;
  if (!div) return;
  const obj = { number: oldValue.count };
  const prefix = value.more ? "+" : "";
  gsap.to(obj, {
    duration: 0.8,
    number: value.count,
    onUpdate() {
      div.innerText = prefix + obj.number.toFixed(0);
    },
  });
});
</script>

<style scoped>
.header {
  background-color: #0000001a;
  -webkit-backdrop-filter: blur(7px);
  backdrop-filter: blur(7px);
}

.last {
  position: relative;
  background-size: cover;
  background-position: center;
  transition: background-image 0.5s ease-in-out;
}
</style>
