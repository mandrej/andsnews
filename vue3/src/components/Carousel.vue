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
      :spaceBetween="30"
      :keyboard="true"
      :grabCursor="true"
      :hashNavigation="{
        watchState: true,
        replaceState: true,
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
      :slides-per-view="1"
      @swiper="onSwiper"
      @hashChange="onHashChange"
      @slideChange="onSlideChange"
    >
      <swiper-slide v-for="obj in objects" :key="obj.id" :data-hash="obj.id">
        <div class="bg-grey-10 absolute-top text-white text-center q-pa-sm">
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
import { Lazy, Navigation, Zoom, Keyboard } from "swiper";

import "swiper/scss";
import "swiper/scss/lazy";
import "swiper/scss/zoom";
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
      let ratio = 1
      if (swiperRef.value && dim) {
        const DIM = [swiperRef.value.width, swiperRef.value.height]
        if (dim[0] >= dim[1]) {
          ratio = dim[0] / DIM[0]
        } else {
          ratio = dim[1] / DIM[1]
        }
        if (ratio < 1) ratio = 1
        return ratio
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
      modules: [Lazy, Navigation, Zoom, Keyboard],
      onSwiper: (sw) => {
        swiperRef.value = sw
        // swDim.value = [sw.el.clientWidth, sw.el.clientHeight]
        const index = hashArray.indexOf(currentId.value)
        sw.slideTo(index)
      },
      zoomRatio,
      onSlideChange: (sw) => {
        const hash = sw.slides[sw.activeIndex].dataset.hash;
        // console.log('currentId ', hash);
      },
      onHashChange: (sw) => {
        const hash = sw.slides[sw.activeIndex].dataset.hash;
        // console.log('hash ', hash);
      }
    };
  },
});
</script>

<style scoped>
.swiper {
  width: 100%;
  height: 100%;
  overflow: hidden;
  /* --swiper-navigation-color: "#fff"; */
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
