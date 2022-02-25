<template>
  <q-dialog
    ref="dialogRef"
    v-model="close"
    @hide="onDialogHide"
    transition-show="slide-up"
    transition-hide="slide-down"
    persistent
  >
    <q-card class="q-dialog-plugin">
      <q-card-section>
        <div class="text-h6">Confirm Delete</div>
      </q-card-section>
      <q-separator />
      <q-card-section>Would you like to delete {{ headline }}?</q-card-section>
      <q-card-actions class="row justify-between q-pa-md q-col-gutter-md">
        <div class="col">
          <q-btn color="primary" label="OK" @click="onOKClick" />
        </div>
        <div class="col text-right">
          <q-btn flat label="Close" @click="onCancelClick" />
        </div>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import { defineComponent, onMounted, ref } from "vue";
import { useDialogPluginComponent } from 'quasar'

export default defineComponent({
  name: "Confirm",
  props: { headline: String },
  emits: [
    ...useDialogPluginComponent.emits
  ],
  setup(props) {
    const close = ref(null)
    const headline = ref(props.headline)
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

    onMounted(() => {
      window.onpopstate = function () {
        if (close.value) close.value = false
      }
    })

    return {
      close,
      headline,
      dialogRef,
      onDialogHide,
      onOKClick() {
        onDialogOK()
      },
      onCancelClick: onDialogCancel
    };
  },
});
</script>
