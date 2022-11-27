<template>
  <q-dialog
    v-model="app.showCarousel"
    :maximized="true"
    transition-show="slide-up"
    transition-hide="slide-down"
    persistent
  >
    <swiper
      :keyboard="true"
      :grab-cursor="true"
      :lazy="{
        loadOnTransitionStart: true,
        loadPrevNext: 3,
      }"
      :zoom="{
        maxRatio: 2,
      }"
      :modules="modules"
      @swiper="onSwiper"
      @slide-change="onSlideChange"
      @lazy-image-ready="onImgReady"
    >
      <swiper-slide
        v-for="obj in list"
        :key="obj.filename"
        :data-hash="namePart(obj.filename)"
      >
        <div
          class="absolute-top q-pa-md"
          style="background-color: rgba(0, 0, 0, 0.3); z-index: 1000"
        >
          <div class="q-mr-xl text-white text-center ellipsis">
            {{ obj.headline }}
            <br />
            {{ caption(obj) }}
          </div>
          <q-btn
            class="absolute-top-right text-white q-pa-md"
            icon="close"
            flat
            round
            @click="onCancel"
          />
        </div>
        <div class="swiper-zoom-container">
          <img class="swiper-lazy" :data-src="fullsized + obj.filename" />
          <div class="swiper-lazy-preloader" />
        </div>
      </swiper-slide>
    </swiper>
  </q-dialog>
</template>

<script setup>
import { useQuasar } from "quasar";
import { reactive, ref } from "vue";
import { useAppStore } from "../stores/app";
import { useRoute } from "vue-router";
import { fullsized, notify, namePart, CONFIG } from "../helpers";
import { Swiper, SwiperSlide } from "swiper/vue";
import { Lazy, Zoom, Keyboard } from "swiper";

import "swiper/scss";
import "swiper/scss/lazy";
import "swiper/scss/zoom";

const emit = defineEmits(["carousel-cancel"]);
const props = defineProps({
  filename: String,
  list: Array,
});

const $q = useQuasar();
const app = useAppStore();
const route = useRoute();
const hash = ref(null);
const dimension = reactive({});
const r = new RegExp(/#(.*)?/); // matching string hash

const modules = [Lazy, Zoom, Keyboard];

const onSwiper = (sw) => {
  const index = props.list.findIndex((x) => x.filename === props.filename);
  if (index === -1) {
    notify({
      type: "negative",
      timeout: 10000,
      message: `${props.filename} couldn't be found in first ${CONFIG.limit} records`,
    });
  } else {
    if (index === 0) {
      onSlideChange(sw);
    } else {
      sw.slideTo(index);
    }
  }
};
const onSlideChange = (sw) => {
  let url = route.fullPath;
  const slide = sw.slides[sw.activeIndex];
  hash.value = slide.dataset.hash;
  const sufix = "#" + hash.value;
  if (r.test(url)) {
    url = url.replace(r, sufix);
  } else {
    url += sufix;
  }
  window.history.replaceState(history.state, null, url);
};
const onImgReady = (sw, slideEl, imageEl) => {
  const img = new Image();
  img.src = imageEl.src;

  const container = slideEl.querySelector(".swiper-zoom-container");
  const wRatio = img.width / sw.width;
  const hRatio = img.height / sw.height;
  const filename = img.src.replace(fullsized, "");
  container.dataset.swiperZoom = Math.max(wRatio, hRatio, 1);
  dimension[filename] = img.width + "x" + img.height;
};
const caption = (rec) => {
  const { aperture, shutter, iso, model, lens } = rec;
  let tmp = "";
  tmp += aperture ? " f" + aperture : "";
  tmp += shutter ? " " + shutter + "s" : "";
  tmp += iso ? " " + iso + " ASA" : "";
  if ($q.screen.gt.sm) {
    tmp += model ? " " + model : "";
    tmp += lens ? " " + lens : "";
    tmp += rec.id ? ", " : "";
    tmp += dimension[rec.filename];
  }
  return tmp;
};

window.onpopstate = function () {
  emit("carousel-cancel", hash.value);
  app.showCarousel = false;
};
const onCancel = () => {
  window.history.replaceState(
    history.state,
    null,
    route.fullPath.replace(r, "")
  );
  emit("carousel-cancel", hash.value);
  app.showCarousel = false;
};
</script>

<style scoped>
.swiper {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: rgb(0.3, 0.3, 0.3) !important;
}
</style>
