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

<script setup>
import { format } from 'quasar'
import { onMounted, computed } from "vue";
import { useAppStore } from "../store/app";
import { useDialogPluginComponent } from 'quasar'

const { humanStorageSize } = format

// eslint-disable-next-line no-undef
defineEmits([...useDialogPluginComponent.emits])
const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

const app = useAppStore();
const tmp = computed(() => app.current)

onMounted(() => {
  window.onpopstate = function () {
    onDialogCancel()
  }
})
const onCancelClick = () => {
  if (window.history.length) window.history.back()
  return onDialogCancel()
}
const onOKClick = () => {
  onDialogOK()
}
</script>
