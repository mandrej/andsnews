<template>
  <q-dialog
    ref="dialogRef"
    :maximized="true"
    transition-show="slide-up"
    transition-hide="slide-down"
    @hide="onDialogHide"
  >
    <swiper
      class="bg-grey-10 text-white"
      :css-mode="true"
      :keyboard="true"
      :grab-cursor="true"
      :hash-navigation="{
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
      :modules="modules"
      @swiper="onSwiper"
      @slide-change="onSlideChange"
    >
      <swiper-slide v-for="obj in objects" :key="obj.id" :data-hash="obj.id">
        <div class="absolute-top text-white text-center q-pa-sm" style="z-index: 1000;">
          <div class="text-subtitle2 ellipsis q-mx-xl">{{ obj.headline }}</div>
          <div class="q-mx-xl text-body2 ellipsis">{{ caption(obj) }}</div>
          <q-btn class="absolute-right" size="lg" icon="close" flat round @click="onCancelClick" />
        </div>
        <div class="swiper-zoom-container" :data-swiper-zoom="zoomRatio(obj.dim)">
          <img class="swiper-lazy" :data-src="fullsized + obj.filename" />
          <div class="swiper-lazy-preloader" />
        </div>
      </swiper-slide>
    </swiper>
  </q-dialog>
</template>

<script>
import { computed, onMounted, ref } from "vue";
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

export default {
  name: "CarouselDialog",
  components: {
    Swiper,
    SwiperSlide,
  },
  props: {
    pid: {
      type: Number,
      required: true
    }
  },
  emits: [
    ...useDialogPluginComponent.emits
  ],
  setup(props, context) {
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

    const store = useStore();
    const objects = computed(() => store.state.app.objects);
    const swiperRef = ref(null)
    const hash = ref(props.pid)
    const index = objects.value.findIndex(x => x.id === props.pid)

    onMounted(() => {
      window.onpopstate = function () {
        onDialogCancel()
      }
    })

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

    const onSlideChange = (sw) => {
      const slide = sw.slides[sw.activeIndex]
      hash.value = slide.dataset.hash
    }
    const onCancelClick = () => {
      window.history.back()
      context.emit('ok', hash.value)
      return onDialogCancel()
    }

    return {
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
      onCancelClick,

      swiperRef,
      modules: [Lazy, Navigation, HashNavigation, Pagination, Zoom, Keyboard],
      onSwiper: (sw) => {
        swiperRef.value = sw
        if (index === -1) {
          notify({ type: "negative", message: `${props.pid} couldn't be found` })
        } else {
          sw.slideTo(index)
        }
      },
      zoomRatio,
      onSlideChange,
    };
  },
}
</script>

<style scoped>
.swiper {
  width: 100%;
  height: 100%;
  overflow: hidden;
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
