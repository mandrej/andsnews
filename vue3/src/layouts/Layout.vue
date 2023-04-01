<template>
  <q-layout v-if="route.meta.plain" view="hHh lpR fFf">
    <q-page-container>
      <q-page class="row">
        <q-page-sticky
          v-show="user.isAuthorized"
          position="top-left"
          :offset="[16, 16]"
          style="z-index: 1000"
        >
          <q-btn fab icon="add" color="warning" to="/add" />
        </q-page-sticky>

        <q-responsive
          :ratio="1"
          class="col-xs-12 col-sm-6 last"
          :style="styling"
        >
          <a
            v-if="last"
            :href="last.href"
            v-ripple.early="{ color: 'purple' }"
            style="display: block"
          />
        </q-responsive>

        <div class="col-xs-12 col-sm-6">
          <q-toolbar class="bg-grey-8 text-white q-pa-md">
            <q-toolbar-title class="text-h4" style="line-height: 100%">
              {{ title }}
              <br />
              <span class="text-body1"
                >{{ bucketInfo.count }} photos since 2007 and counting</span
              >
            </q-toolbar-title>
            <q-btn
              v-if="app.find && Object.keys(app.find).length"
              size="2em"
              flat
              round
              icon="history"
              :to="{ name: 'list', query: app.find }"
            />
          </q-toolbar>

          <router-view />
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
  <!--  -->
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
          icon="history"
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
import { useAuthStore } from "../stores/auth";
import { useRoute } from "vue-router";
import { fullsized, smallsized, fileBroken, version } from "../helpers";

import Find from "../components/Find.vue";
import Menu from "../components/Menu.vue";

const Stat = defineAsyncComponent(() => import("../components/Stat.vue"));

const app = useAppStore();
const auth = useAuthStore();
const route = useRoute();

const user = computed(() => auth.user);
const last = computed(() => app.last);
const title = computed(() => route.meta.title);
const bucketInfo = computed(() => app.bucket);
const busy = computed(() => app.busy);
const drawer = ref(false);
const counter = computed(() => app.counter);

const styling = computed(() => {
  if (last.value) {
    const low = smallsized + last.value.filename;
    const high = fullsized + last.value.filename;
    return "background-image: url(" + high + "), url(" + low + ")";
  }
  return "background-image: url(" + fileBroken + ")";
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
