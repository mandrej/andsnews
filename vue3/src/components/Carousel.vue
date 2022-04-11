<template>
  <q-dialog
    ref="dialogRef"
    :maximized="true"
    transition-show="slide-up"
    transition-hide="slide-down"
    @hide="onDialogHide"
  >
    <swiper
      :keyboard="true"
      :grab-cursor="true"
      :hash-navigation="{
        watchState: true,
        replaceState: false,
      }"
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
    >
      <swiper-slide v-for="obj in objects" :key="obj.id" :data-hash="obj.id">
        <div
          class="absolute-top q-pa-md"
          style="background-color: rgba(0, 0, 0, 0.5); z-index: 1000"
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
            @click="onCancelClick"
          />
        </div>
        <div
          class="swiper-zoom-container"
          :data-swiper-zoom="zoomRatio(obj.dim)"
        >
          <img class="swiper-lazy" :data-src="fullsized + obj.filename" />
          <div class="swiper-lazy-preloader" />
        </div>
      </swiper-slide>
    </swiper>
  </q-dialog>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useDialogPluginComponent } from "quasar";
import { useAppStore } from "../stores/app";
import { fullsized, notify } from "../helpers";
import { Swiper, SwiperSlide } from "swiper/vue";
import { Lazy, HashNavigation, Zoom, Keyboard } from "swiper";

import "swiper/scss";
import "swiper/scss/lazy";
import "swiper/scss/zoom";

// eslint-disable-next-line no-undef
const props = defineProps({
  pid: {
    type: Number,
    required: true,
  },
});
// eslint-disable-next-line no-undef
const emit = defineEmits([...useDialogPluginComponent.emits]);
// eslint-disable-next-line no-unused-vars
const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
  useDialogPluginComponent();

const app = useAppStore();
const objects = computed(() => app.objects);
const swiperRef = ref(null);
const hash = ref(props.pid);
const index = objects.value.findIndex((x) => x.id === props.pid);

const modules = [Lazy, HashNavigation, Zoom, Keyboard];

const onSwiper = (sw) => {
  swiperRef.value = sw;
  if (index === -1) {
    notify({ type: "negative", message: `${props.pid} couldn't be found` });
  } else {
    sw.slideTo(index);
  }
};
const onSlideChange = (sw) => {
  const slide = sw.slides[sw.activeIndex];
  hash.value = slide.dataset.hash;
};
const zoomRatio = (dim) => {
  if (swiperRef.value && dim) {
    const wRatio = dim[0] / swiperRef.value.width;
    const hRatio = dim[1] / swiperRef.value.height;
    return Math.max(wRatio, hRatio, 1);
  }
  return 2;
};
const caption = (rec) => {
  const { aperture, shutter, iso, model, lens } = rec;
  let tmp = "";
  tmp += aperture ? " f" + aperture : "";
  tmp += shutter ? " " + shutter + "s" : "";
  tmp += iso ? " " + iso + " ASA" : "";
  tmp += model ? " " + model : "";
  tmp += lens ? " " + lens : "";
  return tmp;
};

onMounted(() => {
  window.onpopstate = function (e) {
    emit("ok", hash.value);
    onDialogCancel();
  };
});
const onCancelClick = () => {
  if (window.history.length) window.history.back();
  emit("ok", hash.value);
  onDialogCancel();
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
