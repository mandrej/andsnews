<template>
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
      <span v-for="(year, index) in values.year" :key="index">
        <template v-if="index <= limit">
          <router-link
            :key="year"
            :title="year"
            :to="{ path: '/list', query: { year: year } }"
            class="q-px-sm text-black"
            style="display: inline-block; text-decoration: none"
          >{{ year }}</router-link>
        </template>
      </span>
    </div>
    <div class="q-px-md text-subtitle1 gt-sm">
      <router-link
        v-for="tag in values.tags"
        :key="tag"
        :title="tag"
        :to="{ path: '/list', query: { tags: tag } }"
        class="q-pr-sm text-black"
        style="display: inline-block; text-decoration: none"
      >{{ tag }}</router-link>
    </div>
    <q-resize-observer :debounce="300" @resize="onResize" />
  </div>
</template>

<script setup>
import { useQuasar } from 'quasar'
import { onMounted, computed, ref } from 'vue'
import { useAppStore } from "../store/app";
import { useAuthStore } from "../store/auth";

const $q = useQuasar()
const app = useAppStore();
const auth = useAuthStore();
const report = ref(null)

const values = computed(() => app.values)
const limit = ref(99)
if ($q.screen.xs) {
  limit.value = 9
}
const nickNames = computed(() => app.nickNames)

onMounted(() => {
  auth.getPermission()
})
// eslint-disable-next-line no-unused-vars
const onResize = (size) => {
  // console.log(size);
  if ($q.screen.xs) {
    limit.value = 9
  } else {
    limit.value = 99
  }
}
</script>

