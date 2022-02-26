<template>
  <q-dialog
    ref="dialogRef"
    v-model="close"
    @hide="onDialogHide"
    transition-show="slide-down"
    transition-hide="slide-up"
    persistent
  >
    <q-card class="q-dialog-plugin">
      <q-card-section>
        <div class="text-h6">Confirm Delete</div>
      </q-card-section>
      <q-separator />
      <q-card-section>Would you like to delete {{ props.headline }}?</q-card-section>
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
import { onMounted, ref } from "vue";
import { useDialogPluginComponent } from 'quasar'

export default {
  name: "Confirm",
  props: { headline: String },
  emits: [
    ...useDialogPluginComponent.emits
  ],
  setup(props) {
    const close = ref(null)
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

    onMounted(() => {
      window.onpopstate = function () {
        if (close.value) close.value = false
      }
    })

    return {
      close,
      props,
      dialogRef,
      onDialogHide,
      onOKClick() {
        onDialogOK()
      },
      onCancelClick: onDialogCancel
    };
  },
};
</script>
