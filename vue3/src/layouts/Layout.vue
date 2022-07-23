<template>
  <q-layout v-if="route.meta.plain" view="hHh lpR fFf">
    <q-page-container>
      <q-page class="row">
        <q-responsive
          :ratio="1.75"
          class="col-xs-12 col-sm-6 last"
          :style="styling"
        />
        <div class="col-xs-12 col-sm-6">
          <div class="row bg-grey-10 text-white q-pa-md">
            <div class="col text-h4">
              {{ title }}
              <br />
              <span class="text-body1"
                >{{ bucketInfo.count }} photos since 2007 and counting</span
              >
            </div>
            <q-btn
              v-if="app.find && Object.keys(app.find).length"
              class="col-1"
              flat
              round
              icon="grid_view"
              :to="{ name: 'list', query: app.find }"
            />
          </div>
          <router-view />
          <div class="absolute-bottom q-pa-md text-right">{{ version }}</div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
  <q-layout v-else view="hHh Lpr lFf">
    <q-header class="fixed-top">
      <q-toolbar class="bg-grey-8 text-white">
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

        <div v-if="route.name === 'list'">
          {{ counter.more ? "+" : "" }}{{ counter.count }}
        </div>
        <q-btn
          v-else
          flat
          round
          icon="grid_view"
          :to="{ name: 'list', query: app.find }"
        >
        </q-btn>
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
      dark
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
import { defineAsyncComponent, computed, ref } from "vue";
import { useAppStore } from "../stores/app";
import { useRoute } from "vue-router";
import { fullsized, smallsized } from "../helpers";

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

const styling = computed(() => {
  const low = smallsized + last.value;
  const high = fullsized + last.value;
  return "background-image: url(" + high + "), url(" + low + ")";
});
const version = computed(() => {
  const ver = process.env.ANDS_VERSION.match(/.{1,4}/g).join(".");
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
</script>

<style scoped>
.last {
  position: relative;
  background-size: cover;
  background-position: center;
  transition: background-image 0.5s ease-in-out;
}
</style>
