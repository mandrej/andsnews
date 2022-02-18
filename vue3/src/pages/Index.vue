<template>
  <q-page class="full-height last" :style="styling">
    <div class="text-subtitle1 q-pa-md text-white text-right">
      ANDрејевићи personal photo album
      <br />
      {{ bucketInfo.count }} photos since 2007 and counting
    </div>
    <div class="absolute-bottom">
      <div class="q-pa-sm text-h4">
        <router-link
          v-for="nick in nickNames"
          :key="nick"
          :title="nick"
          :to="{ path: '/list', query: { nick: nick } }"
          class="q-px-sm text-white"
          style="display: inline-block; text-decoration: none"
        >{{ nick }}</router-link>
      </div>
      <div class="q-pa-sm text-h5">
        <router-link
          v-for="year in values.year"
          :key="year"
          :title="year"
          :to="{ path: '/list', query: { year: year } }"
          class="q-px-sm text-white"
          style="display: inline-block; text-decoration: none"
        >{{ year }}</router-link>
      </div>
      <div class="q-px-md text-subtitle1">
        <router-link
          v-for="tag in values.tags"
          :key="tag"
          :title="tag"
          :to="{ path: '/list', query: { tags: tag } }"
          class="q-pr-sm text-white"
          style="display: inline-block; text-decoration: none"
        >{{ tag }}</router-link>
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent, computed, onMounted } from "vue";
import { useStore } from "vuex";
import { fullsized, smallsized } from "../helpers";

export default defineComponent({
  name: "Home",
  setup() {
    const store = useStore();

    const last = computed(() => store.state.app.last);
    const styling = computed(() => {
      const low = smallsized + last.value.filename;
      const high = fullsized + last.value.filename;
      return "background-image: url(" + high + "), url(" + low + ")";
    });

    onMounted(() => {
      store.dispatch('auth/getPermission')
    })

    return {
      last,
      styling,
      values: computed(() => store.state.app.values),
      nickNames: computed(() => store.getters["app/nickNames"]),
      bucketInfo: computed(() => store.state.app.bucket),
    };
  },
});
</script>

<style scoped>
.last {
  background-size: cover;
  background-position: center;
  transition: background-image 0.5s ease-in-out;
}
</style>
