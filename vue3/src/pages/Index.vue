<template>
  <q-page class="row">
    <div class="col-xs-12 col-sm-6 last" :style="styling"></div>
    <div class="col-xs-12 col-sm-6">
      <div class="q-pa-md">
        <div class="text-h4">{{ title }} personal photo album</div>
        <div class="text-h6">{{ bucketInfo.count }} photos since 2007 and counting</div>
      </div>
      <div>
        <div class="q-pa-sm text-h4">
          <router-link
            v-for="nick in nickNames"
            :key="nick"
            :title="nick"
            :to="{ path: '/list', query: { nick: nick } }"
            class="q-px-sm text-black"
            style="display: inline-block; text-decoration: none"
          >{{ nick }}</router-link>
        </div>
        <div class="q-pa-sm text-h5">
          <router-link
            v-for="year in values.year"
            :key="year"
            :title="year"
            :to="{ path: '/list', query: { year: year } }"
            class="q-px-sm text-black"
            style="display: inline-block; text-decoration: none"
          >{{ year }}</router-link>
        </div>
        <div class="q-px-md text-subtitle1 gt-xs">
          <router-link
            v-for="tag in values.tags"
            :key="tag"
            :title="tag"
            :to="{ path: '/list', query: { tags: tag } }"
            class="q-pr-sm text-black"
            style="display: inline-block; text-decoration: none"
          >{{ tag }}</router-link>
        </div>
        <div class="absolute-bottom q-pa-md text-right">{{ version }}</div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useStore } from "vuex";
import { useRoute } from "vue-router";
import { fullsized, smallsized } from "../helpers";

const store = useStore();
const route = useRoute();
const last = computed(() => store.state.app.last);
const styling = computed(() => {
  const low = smallsized + last.value.filename;
  const high = fullsized + last.value.filename;
  return "background-image: url(" + high + "), url(" + low + ")";
});
const values = computed(() => store.state.app.values)
const nickNames = computed(() => store.getters["app/nickNames"])
const bucketInfo = computed(() => store.state.app.bucket)

onMounted(() => {
  store.dispatch('auth/getPermission')
})
const title = computed(() => route.meta.title || 'ANDрејевићи')
const version = computed(() => {
  const ver = import.meta.env.VUE_APP_VERSION.match(/.{1,4}/g).join(".");
  return "© 2007 - " + ver;
});
</script>

<style scoped>
.last {
  background-size: cover;
  background-position: center;
  transition: background-image 0.5s ease-in-out;
}
</style>
