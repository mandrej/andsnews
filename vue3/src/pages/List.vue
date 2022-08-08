<template>
  <Edit v-if="app.showEdit" :rec="current.obj" @editOk="editOk" />
  <Confirm v-if="app.showConfirm" :rec="current.obj" />
  <Carousel
    v-if="app.showCarousel"
    :pid="current.pid"
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

    <div
      v-for="(list, datum) in objectsByDate"
      :key="datum"
      class="q-pa-md scroll overflow-hidden"
    >
      <div
        class="text-h6 text-weight-light"
        :class="busy && start ? 'blur' : ''"
      >
        {{ formatDatum(datum, "dddd DD.MM.YYYY") }}
      </div>
      <transition-group tag="div" class="row q-col-gutter-md" name="fade">
        <div
          v-for="item in list"
          :key="item.id"
          class="col-xs-12 col-sm-6 col-md-4 col-lg-3 col-xl-2"
        >
          <q-card
            :id="'card' + item.id"
            class="bg-grey-2"
            :class="busy && start ? 'blur' : ''"
            flat
          >
            <q-img
              class="cursor-pointer"
              :ratio="5 / 4"
              :src="smallsized + item.filename"
              @click="
                carousel(item.id);
                analytics('popular-picture', item.filename);
              "
            >
              <template #error>
                <img src="/broken.svg" />
              </template>
              <div class="absolute-bottom text-subtitle2">
                {{ item.headline }}
              </div>
            </q-img>
            <q-card-section class="row justify-between q-py-none">
              <div style="line-height: 42px">
                {{ item.nick }},
                <router-link
                  :to="{
                    path: '/list',
                    query: {
                      year: item.year,
                      month: item.month,
                      day: item.day,
                    },
                  }"
                  class="text-secondary"
                  style="text-decoration: none"
                  >{{ formatDatum(item.date, "DD.MM.YYYY") }}</router-link
                >
                {{ item.date.substring(11) }}
              </div>
              <q-btn
                v-if="item.loc"
                flat
                round
                color="grey"
                icon="my_location"
                target="blank"
                :href="
                  'https://www.google.com/maps/search/?api=1&query=' +
                  [...item.loc]
                "
              />
            </q-card-section>
            <q-card-actions
              v-if="user.isAuthorized"
              class="justify-between q-pt-none"
            >
              <q-btn
                v-if="isAuthorOrAdmin(item)"
                flat
                round
                color="grey"
                icon="delete"
                @click="confirm(item)"
              />
              <q-btn
                v-if="isAuthorOrAdmin(item)"
                flat
                round
                color="grey"
                icon="edit"
                @click="edit(item)"
              />
              <q-btn
                v-if="isAuthorOrAdmin(item)"
                flat
                round
                color="grey"
                icon="share"
                @click="onShare(item.id)"
              />
              <q-btn
                flat
                round
                color="grey"
                icon="download"
                :href="`/api/download/${item.filename}`"
                :download="item.filename"
                @click.stop="analytics('download-picture', item.filename)"
              />
            </q-card-actions>
          </q-card>
        </div>
      </transition-group>
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
import { copyToClipboard, scroll, throttle } from "quasar";
import {
  defineAsyncComponent,
  onMounted,
  onUpdated,
  computed,
  reactive,
  ref,
} from "vue";
import { useAppStore } from "../stores/app";
import { useAuthStore } from "../stores/auth";
import { useRoute } from "vue-router";
import { smallsized, formatDatum, notify } from "../helpers";
import Carousel from "../components/Carousel.vue";

const Edit = defineAsyncComponent(() => import("../components/Edit.vue"));
const Confirm = defineAsyncComponent(() => import("../components/Confirm.vue"));

const { getScrollTarget, setVerticalScrollPosition } = scroll;

const app = useAppStore();
const auth = useAuthStore();
const route = useRoute();
const next = computed(() => app.next);
const error = computed(() => app.error);
const objectsByDate = computed(() => app.objectsByDate);
const user = computed(() => auth.user);

const busy = computed(() => app.busy);
const start = ref(true);
const current = reactive({ obj: null, pid: 0 });

onMounted(() => {
  const hash = route.hash;
  if (hash) {
    setTimeout(() => {
      carousel(+hash.substring(1));
    }, 1000);
  }
});

onUpdated(() => {
  start.value = true;
  console.log("onUpdated ", busy.value);
});

const isAuthorOrAdmin = (rec) => {
  return user.value.isAdmin || user.value.email === rec.email;
};

const scrollHandler = throttle((obj) => {
  // trottle until busy: true
  start.value = false;
  const scrollHeight = document.documentElement.scrollHeight;
  if (
    scrollHeight - obj.position.top < 3000 &&
    obj.direction === "down" &&
    next.value
  ) {
    app.fetchRecords();
  }
}, 500);

const analytics = (event_name, file_name) => {
  /**
   * popular-picture
   * download-picture
   *
   */
  gtag("event", event_name, {
    filename: file_name,
    user: user.value && user.value.email ? user.value.email : "anonymous",
    count: 1,
  });
};

const edit = (rec) => {
  current.obj = rec;
  window.history.pushState(history.state, null, route.fullPath); // fake history
  app.showEdit = true;
};
const editOk = (id) => {
  start.value = false;
  const el = document.querySelector("#card" + id);
  if (!el) return;
  el.classList.add("bounce");
  setTimeout(() => {
    el.classList.remove("bounce");
  }, 2000);
};
const confirm = (rec) => {
  current.obj = rec;
  window.history.pushState(history.state, null, route.fullPath); // fake history
  app.showConfirm = true;
};
const carousel = (id) => {
  current.pid = id;
  window.history.pushState(history.state, null, route.fullPath); // fake history
  app.showCarousel = true;
};
const carouselCancel = (hash) => {
  start.value = false;
  const el = document.querySelector("#card" + hash);
  if (!el) return;
  const target = getScrollTarget(el);
  setVerticalScrollPosition(target, el.offsetTop, 500);
};
const onShare = (id) => {
  const url = window.location.href + "#" + id;
  copyToClipboard(url)
    .then(() => {
      notify({ type: "info", message: "URL copied to clipboard" });
    })
    .catch(() => {
      notify({ type: "warning", message: "Unable to copy URL to clipboard" });
    });
};
</script>

<style scoped>
.blur {
  filter: blur(1rem);
}
</style>
