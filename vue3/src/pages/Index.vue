<template>
  <div class="q-pa-sm text-h4">
    <router-link
      v-for="obj in nickCountValues"
      :key="obj.value"
      :title="obj.value + ': ' + obj.count"
      :to="{ path: '/list', query: { nick: obj.value } }"
      class="q-px-sm text-black link"
      >{{ obj.value }}</router-link
    >
  </div>
  <div class="q-pa-sm text-h5">
    <span v-for="(obj, index) in values.year" :key="index">
      <template v-if="index <= limit">
        <router-link
          :key="obj.value"
          :title="obj.value + ': ' + obj.count"
          :to="{ path: '/list', query: { year: obj.value } }"
          class="q-px-sm text-black link"
          >{{ obj.value }}</router-link
        >
      </template>
    </span>
  </div>
  <div class="q-px-md text-subtitle1 gt-sm">
    <router-link
      v-for="obj in values.tags"
      :key="obj.value"
      :title="obj.value + ': ' + obj.count"
      :to="{ path: '/list', query: { tags: obj.value } }"
      class="q-pr-sm text-black link"
      >{{ obj.value }}</router-link
    >
  </div>
  <q-resize-observer :debounce="300" @resize="onResize" />
</template>

<script setup>
import { useQuasar } from "quasar";
import { onMounted, computed, ref } from "vue";
import { useAppStore } from "../stores/app";
import { useAuthStore } from "../stores/auth";

const $q = useQuasar();
const app = useAppStore();
const auth = useAuthStore();

const values = computed(() => app.values);
const nickCountValues = computed(() => app.nickCountValues);
const limit = ref(99);
if ($q.screen.xs) {
  limit.value = 9;
}
onMounted(() => {
  auth.getPermission();
});
// eslint-disable-next-line no-unused-vars
const onResize = (size) => {
  if ($q.screen.xs) {
    limit.value = 9;
  } else {
    limit.value = 99;
  }
};
</script>

<style scoped>
.link {
  display: inline-block;
  text-decoration: none;
}
</style>
