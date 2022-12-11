<template>
  <Edit v-if="app.showEdit" :rec="current" @editOk="editOk" />
  <Confirm v-if="app.showConfirm" :rec="current" @closeConfirm="confirmOk" />
  <Carousel
    v-if="app.showCarousel"
    :filename="currentFileName"
    :list="objects"
    @carouselCancel="carouselCancel"
  />

  <q-page>
    <q-banner
      v-if="error"
      class="absolute-center text-center bg-warning q-pa-md"
      rounded
    >
      <q-icon name="error_outline" size="4em" />
      <div class="text-h6">Something went wrong ...</div>
      <div>{{ error }}</div>
    </q-banner>
    <q-banner
      v-else-if="error === 0"
      class="absolute-center text-center bg-warning q-pa-md"
      rounded
    >
      <q-icon name="error_outline" size="4em" />
      <div class="text-h6">No data found</div>
      <div>for current filter/ search</div>
    </q-banner>

    <q-scroll-observer
      @scroll="scrollHandler"
      axis="vertical"
      :debounce="500"
    />

    <div class="q-pa-md">
      <div v-for="(list, datum) in objectsByDate" :key="datum" class="q-mb-md">
        <div class="gt-xs text-h6 text-weight-light text-secondary">
          {{ formatDatum(datum, "dddd DD.MM.YYYY") }}
        </div>
        <transition-group tag="div" class="row q-col-gutter-md" name="fade">
          <div
            v-for="item in list"
            :key="item.id"
            class="col-xs-12 col-sm-6 col-md-4 col-lg-3 col-xl-2"
          >
            <Card
              :rec="item"
              @invokeCarousel="carouselShow"
              @confirmDelete="confirm"
              @editRecord="edit"
            />
          </div>
        </transition-group>
      </div>
    </div>

    <q-page-scroller
      position="bottom-right"
      :scroll-offset="150"
      :offset="[18, 18]"
    >
      <q-btn fab icon="arrow_upward" color="warning" />
    </q-page-scroller>
  </q-page>
</template>

<script setup>
import { scroll, throttle } from "quasar";
import { defineAsyncComponent, onMounted, computed, ref } from "vue";
import { useAppStore } from "../stores/app";
import { useRoute } from "vue-router";
import { formatDatum } from "../helpers";

import Card from "../components/Card.vue";
import Carousel from "../components/Carousel.vue";

const Edit = defineAsyncComponent(() => import("../components/Edit.vue"));
const Confirm = defineAsyncComponent(() => import("../components/Confirm.vue"));

const { getScrollTarget, setVerticalScrollPosition } = scroll;

const app = useAppStore();
const route = useRoute();
const next = computed(() => app.next);
const error = computed(() => app.error);
const objects = computed(() => app.objects);
const objectsByDate = computed(() => app.objectsByDate);

const current = computed(() => app.current);
const currentFileName = ref(null);

onMounted(() => {
  const hash = route.hash;
  if (hash) {
    const filename = hash.substring(2);
    setTimeout(() => {
      carouselShow(filename);
    }, 1000);
  }
});

const scrollHandler = throttle((obj) => {
  // trottle until busy: true
  const scrollHeight = document.documentElement.scrollHeight;
  if (
    scrollHeight - obj.position.top < 3000 &&
    obj.direction === "down" &&
    next.value
  ) {
    app.fetchRecords();
  }
}, 500);

const edit = (rec) => {
  app.current = rec;
  window.history.pushState(history.state, null, route.fullPath); // fake history
  app.showEdit = true;
};
const editOk = (hash) => {
  const el = document.querySelector("#" + hash);
  if (!el) return;
  el.classList.add("bounce");
  setTimeout(() => {
    el.classList.remove("bounce");
  }, 2000);
};
const confirm = (rec) => {
  app.current = rec;
  window.history.pushState(history.state, null, route.fullPath); // fake history
  app.showConfirm = true;
};
const confirmOk = (rec) => {
  app.showConfirm = false;
  app.deleteRecord(rec);
};
const carouselShow = (filename) => {
  currentFileName.value = filename;
  window.history.pushState(history.state, null, route.fullPath); // fake history
  app.showCarousel = true;
};
const carouselCancel = (hash) => {
  const el = document.querySelector("#" + hash);
  if (!el) return;
  const target = getScrollTarget(el);
  setVerticalScrollPosition(target, el.offsetTop, 500);
};
</script>
