<template>
  <q-dialog
    ref="dialogRef"
    transition-show="slide-down"
    transition-hide="slide-up"
    persistent
    @hide="onDialogHide"
  >
    <q-card class="q-dialog-plugin">
      <q-toolbar class="bg-grey-2 text-black row justify-between" bordered>
        <q-toolbar-title>Confirm Delete</q-toolbar-title>
      </q-toolbar>
      <q-card-section>Would you like to delete {{ humanStorageSize(tmp.size) }} image named "{{ tmp.headline }}"?</q-card-section>
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
import { format } from 'quasar'
import { onMounted, computed } from "vue";
import { useStore } from "vuex";
import { useDialogPluginComponent } from 'quasar'

const { humanStorageSize } = format

export default {
  name: "ConfirmDialog",
  emits: [
    ...useDialogPluginComponent.emits
  ],
  setup() {
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

    const store = useStore();
    const tmp = computed(() => store.state.app.current)

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
      tmp,
      humanStorageSize,
      close,
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
