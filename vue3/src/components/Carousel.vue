<template>
  <q-dialog
    ref="dialogRef"
    @hide="onDialogHide"
    transition-show="slide-up"
    transition-hide="slide-down"
  >
    <q-card class="column window-width">
      <!-- <q-card-actions>
        <q-btn icon="close" flat round @click="onCancelClick" />
      </q-card-actions>-->
      <q-card-section>
        <q-carousel
          class="bg-black"
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
            v-for="(obj, index) in objects"
            :key="index"
            :img-src="fullsized + obj.filename"
          >
            <div class="bg-white absolute-top text-center">
              <div class="text-h6">{{ obj.headline }}</div>
              <div class="text-subtitle1">f{{ obj.aperture }} {{ obj.shutter }}s ISO {{ obj.iso }}</div>
            </div>
            <q-btn
              class="absolute-top-right q-pa-md"
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


    return {
      dialogRef,
      onDialogHide,

      objects,
      fullsized,
      slide,
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
