<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <q-page class="row">
        <div class="col-xs-12 col-sm-6 last" :style="styling"></div>
        <div class="col-xs-12 col-sm-6">
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
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useStore } from "vuex";
import { fullsized, smallsized } from "../helpers";

const store = useStore();
const route = useRoute();
const router = useRouter();

const last = computed(() => store.state.app.last);
const title = computed(() => route.meta.title || 'ANDрејевићи')
const bucketInfo = computed(() => store.state.app.bucket)

const find = computed(() => store.state.app.find)
const tmp = ref({ ...find.value })

const styling = computed(() => {
  const low = smallsized + last.value.filename;
  const high = fullsized + last.value.filename;
  return "background-image: url(" + high + "), url(" + low + ")";
});
const version = computed(() => {
  const ver = import.meta.env.VUE_APP_VERSION.match(/.{1,4}/g).join(".");
  return "© 2007 - " + ver;
});

// click on router-link
watch(route, (to, old) => setForm(to, old));

const setForm = (to, old) => {
  // if (JSON.stringify(to.query) === JSON.stringify(old.query)) return
  // remove undefined and empty list
  Object.keys(to.query).forEach((key) => {
    if (to.query[key] == null || to.query[key].length === 0) {
      delete to.query[key];
    }
  });
  // adopt to match types in store
  Object.keys(to.query).forEach((key) => {
    if (['year', 'month', 'day'].includes(key)) {
      to.query[key] = +to.query[key]
    }
  });
  store.commit("app/saveFindForm", to.query);

  if (Object.keys(to.query).length) {
    store.commit("app/setBusy", false); // interupt loading
    store.commit("app/resetObjects");
    store.dispatch("app/fetchRecords"); // new filter
    if (to.hash) {
      router.push({ path: "/list", query: tmp.value, hash: to.hash });
    } else {
      router.push({ path: "/list", query: tmp.value });
    }
  }
}
</script>

<style scoped>
.last {
  background-size: cover;
  background-position: center;
  transition: background-image 0.5s ease-in-out;
}
</style>
