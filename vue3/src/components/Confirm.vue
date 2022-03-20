<template>
  <q-dialog
    ref="dialogRef"
    @hide="onDialogHide"
    transition-show="slide-down"
    transition-hide="slide-up"
    persistent
  >
    <q-card class="q-dialog-plugin">
      <q-toolbar class="bg-grey-2 text-black row justify-between" bordered>
        <q-toolbar-title>Confirm Delete</q-toolbar-title>
      </q-toolbar>
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
  props: ['headline'],
  emits: [
    ...useDialogPluginComponent.emits
  ],
  setup(props) {
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

    onMounted(() => {
      window.onpopstate = function () {
        onDialogCancel()
      }
    })
    const onCancelClick = () => {
      window.history.back()
      return onDialogCancel()
    }

    return {
      close,
      props,
      dialogRef,
      onDialogHide,
      onOKClick() {
        onDialogOK()
      },
      onCancelClick,
    };
  },
};
</script>
