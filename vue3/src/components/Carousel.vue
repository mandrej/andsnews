<template>
  <q-dialog
    ref="dialogRef"
    @hide="onDialogHide"
    transition-show="slide-up"
    transition-hide="slide-down"
  >
    <q-card class="column window-width">
      <q-card-section>
        <q-carousel
          class="bg-grey-10"
          v-model="slide"
          v-model:fullscreen="fullscreen"
          transition-prev="slide-right"
          transition-next="slide-left"
          arrows
          animated
          swipeable
          infinite
        >
          <q-carousel-slide
            :name="index"
            :img-src="fullsized + obj.filename"
            v-for="(obj, index) in objects"
            :key="index"
          >
            <div class="bg-grey-10 absolute-top text-white text-center q-pa-sm">
              <div class="text-subtitle2">{{ obj.headline }}</div>
              <div class="text-body2">{{ caption(obj) }}</div>
            </div>
            <q-btn
              class="absolute-top-right q-pa-md text-white"
              icon="close"
              flat
              round
              @click="onCancelClick"
            />
          </q-carousel-slide>
        </q-carousel>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script>
import { defineComponent, computed, ref } from "vue";
import { useDialogPluginComponent } from 'quasar'
import { useStore } from "vuex";
import { fullsized } from "../helpers";

export default defineComponent({
  name: "Carousel",
  props: {
    index: Number
  },
  emits: [
    ...useDialogPluginComponent.emits
  ],
  setup(props) {
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

    const store = useStore();
    const objects = computed(() => store.state.app.objects);
    const slide = ref(props.index);

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

    return {
      dialogRef,
      onDialogHide,

      objects,
      fullsized,
      slide,
      caption,
      fullscreen: ref(true),

      onOKClick() {
        // on OK, it is REQUIRED to
        // call onDialogOK (with optional payload)
        onDialogOK()
        // or with payload: onDialogOK({ ... })
        // ...and it will also hide the dialog automatically
      },
      onCancelClick: onDialogCancel
    };
  },
});
</script>

<style scoped>
.q-carousel__slide {
  background-size: contain;
  background-position: 50%;
  background-repeat: no-repeat;
}
</style>
