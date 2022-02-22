<template>
  <q-dialog
    ref="dialogRef"
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
        <div
          class="absolute-top text-white text-center q-pa-sm"
          style="background-color: rgba(0, 0, 0, 0.5); z-index: 1000;"
        >
          <div class="text-subtitle2">{{ obj.headline }}</div>
          <div class="text-body2">{{ caption(obj) }}</div>
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
import { defineComponent, computed, ref } from "vue";
import { useDialogPluginComponent } from 'quasar'
import { useStore } from "vuex";
import { fullsized } from "../helpers";
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
    const objects = computed(() => store.state.app.objects);
    const hashArray = objects.value.map(item => item.id)
    const currentId = ref(props.pid);
    const swiperRef = ref(null)

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

    return {
      objects,
      fullsized,
      currentId,
      hashArray,
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

      swiperRef,
      onCancelClick: onDialogCancel,
      modules: [Lazy, Navigation, HashNavigation, Pagination, Zoom, Keyboard],
      onSwiper: (sw) => {
        swiperRef.value = sw
        const index = hashArray.indexOf(currentId.value)
        sw.slideTo(index)
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
