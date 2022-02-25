<template>
  <q-dialog
    ref="dialogRef"
    v-model="close"
    @hide="onDialogHide"
    :maximized="true"
    transition-show="slide-up"
    transition-hide="slide-down"
  >
    <swiper
      class="bg-grey-10 text-white"
      :keyboard="true"
      :grabCursor="true"
      :hashNavigation="{
        watchState: true,
        replaceState: true,
      }"
      :pagination="{
        type: 'fraction',
      }"
      :lazy="{
        loadOnTransitionStart: true,
        loadPrevNext: 2
      }"
      :zoom="{
        maxRatio: 2
      }"
      :navigation="true"
      :modules="modules"
      @swiper="onSwiper"
    >
      <swiper-slide v-for="obj in objects" :key="obj.id" :data-hash="obj.id">
        <div class="absolute-top text-white text-center q-pa-sm" style="z-index: 1000;">
          <div class="text-subtitle2 ellipsis">{{ obj.headline }}</div>
          <div class="text-body2 gt-xs ellipsis">{{ caption(obj) }}</div>
        </div>
        <div class="swiper-zoom-container" :data-swiper-zoom="zoomRatio(obj.dim)">
          <img class="swiper-lazy" :data-src="fullsized + obj.filename" />
          <div class="swiper-lazy-preloader"></div>
        </div>
      </swiper-slide>
    </swiper>
  </q-dialog>
</template>

<script>
import { defineComponent, computed, onMounted, ref } from "vue";
import { useDialogPluginComponent } from 'quasar'
import { useStore } from "vuex";
import { fullsized, notify } from "../helpers";
import { Swiper, SwiperSlide } from 'swiper/vue';
import { Lazy, Navigation, HashNavigation, Pagination, Zoom, Keyboard } from "swiper";

import "swiper/scss";
import "swiper/scss/lazy";
import "swiper/scss/zoom";
import "swiper/scss/pagination";
import "swiper/scss/navigation";

export default defineComponent({
  name: "Carousel",
  props: {
    pid: Number
  },
  components: {
    Swiper,
    SwiperSlide,
  },
  emits: [
    ...useDialogPluginComponent.emits
  ],
  setup(props) {
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

    const store = useStore();
    const close = ref(null)
    const objects = computed(() => store.state.app.objects);
    const swiperRef = ref(null)
    const index = objects.value.findIndex(x => x.id === props.pid)

    const caption = (rec) => {
      const { aperture, shutter, iso, model, lens } = rec
      let tmp = ''
      tmp += aperture ? ' f' + aperture : ''
      tmp += shutter ? ' ' + shutter + 's' : ''
      tmp += iso ? ' ' + iso + ' ASA' : ''
      tmp += model ? ' ' + model : ''
      tmp += lens ? ' ' + lens : ''
      return tmp
    }

    const zoomRatio = (dim) => {
      if (swiperRef.value && dim) {
        const wRatio = dim[0] / swiperRef.value.width
        const hRatio = dim[1] / swiperRef.value.height
        return Math.max(wRatio, hRatio, 1)
      }
      return 2
    }

    onMounted(() => {
      window.onpopstate = function () {
        if (close.value) close.value = false
      }
    })

    return {
      close,
      index,
      objects,
      fullsized,
      caption,

      dialogRef,
      onDialogHide,
      onOKClick() {
        // on OK, it is REQUIRED to
        // call onDialogOK (with optional payload)
        onDialogOK()
        // or with payload: onDialogOK({ ... })
        // ...and it will also hide the dialog automatically
      },
      onCancelClick: onDialogCancel,

      swiperRef,
      modules: [Lazy, Navigation, HashNavigation, Pagination, Zoom, Keyboard],
      onSwiper: (sw) => {
        swiperRef.value = sw
        if (index === -1) {
          notify("negative", `${props.pid} couldn't be found`)
        } else {
          sw.slideTo(index)
        }
      },
      zoomRatio,
    };
  },
});
</script>

<style scoped>
.swiper {
  width: 100%;
  height: 100%;
  overflow: hidden;
  --swiper-navigation-color: "#fff";
}

.swiper-slide {
  background-position: center;
  background-size: cover;
  overflow: hidden;
}

.swiper-slide img {
  display: block;
  width: 100%;
  object-fit: contain;
}
</style>
