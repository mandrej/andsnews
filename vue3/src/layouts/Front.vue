<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useStore } from "vuex";

const store = useStore();
const route = useRoute();
const router = useRouter();

const find = computed(() => store.state.app.find)
const tmp = ref({ ...find.value })

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
