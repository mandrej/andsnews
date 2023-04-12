<template>
  <Edit v-if="app.showEdit" :rec="current" @edit-ok="editOk" />
  <Confirm v-if="app.showConfirm" :rec="current" @confirm-ok="confirmOk" />
  <Carousel
    v-if="app.showCarousel"
    :filename="currentFileName"
    :list="objects"
    @carousel-cancel="carouselCancel"
    @confirm-delete="confirmShow"
    @delete-record="app.deleteRecord"
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
      <div v-for="(list, index) in groupObjects" :key="index" class="q-mb-md">
        <transition-group tag="div" class="row q-col-gutter-md" name="fade">
          <div
            v-for="item in list"
            :key="item.id"
            class="col-xs-12 col-sm-6 col-md-4 col-lg-3 col-xl-2"
          >
            <Card
              :rec="item"
              :canManage="isAuthorOrAdmin(item)"
              @carousel-show="carouselShow"
              @edit-record="editRecord"
              @confirm-delete="confirmShow"
              @delete-record="app.deleteRecord"
              @google-analytics="ga"
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
import { useAuthStore } from "../stores/auth";
import { useRoute } from "vue-router";
import { fakeHistory } from "../helpers";

import Card from "../components/Card.vue";
import Carousel from "../components/Carousel.vue";

const Edit = defineAsyncComponent(() => import("../components/Edit.vue"));
const Confirm = defineAsyncComponent(() => import("../components/Confirm.vue"));

const { getScrollTarget, setVerticalScrollPosition } = scroll;

const app = useAppStore();
const auth = useAuthStore();
const user = computed(() => auth.user);
const route = useRoute();
const next = computed(() => app.next);
const error = computed(() => app.error);
const objects = computed(() => app.objects);
const groupObjects = computed(() => app.groupObjects);

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

const isAuthorOrAdmin = (rec) => {
  return user.value.isAdmin || user.value.email === rec.email;
};

const editRecord = (rec) => {
  app.current = rec;
  fakeHistory();
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
const confirmShow = (rec) => {
  app.current = rec;
  fakeHistory();
  app.showConfirm = true;
};
const confirmOk = (rec) => {
  app.showConfirm = false;
  app.deleteRecord(rec);
};
const carouselShow = (filename) => {
  currentFileName.value = filename;
  fakeHistory();
  app.showCarousel = true;
};
const carouselCancel = (hash) => {
  const el = document.querySelector("#" + hash);
  if (!el) return;
  const target = getScrollTarget(el);
  setVerticalScrollPosition(target, el.offsetTop, 500);
};
const ga = (event_name, rec) => {
  /**
   * popular-picture
   * download-picture
   *
   */
  gtag("event", event_name, {
    filename: rec.filename,
    user: user.value && user.value.email ? user.value.email : "anonymous",
    count: 1,
  });
};
</script>
