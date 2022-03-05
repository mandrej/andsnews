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
      <router-link
        v-for="year in values.year"
        :key="year"
        :title="year"
        :to="{ path: '/list', query: { year: year } }"
        class="q-px-sm text-black"
        style="display: inline-block; text-decoration: none"
      >{{ year }}</router-link>
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
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useStore } from "vuex";

const store = useStore();

const values = computed(() => store.state.app.values)
const nickNames = computed(() => store.getters["app/nickNames"])

onMounted(() => {
  store.dispatch('auth/getPermission')
})
</script>

