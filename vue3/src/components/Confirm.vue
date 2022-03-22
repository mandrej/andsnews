<template>
  <q-dialog v-model="show" transition-show="slide-down" transition-hide="slide-up" persistent>
    <q-card class="q-dialog-plugin">
      <q-toolbar class="bg-grey-2 text-black row justify-between" bordered>
        <q-toolbar-title>Confirm Delete</q-toolbar-title>
      </q-toolbar>
      <q-card-section>Would you like to delete {{ rec.headline }}?</q-card-section>
      <q-card-actions class="row justify-between q-pa-md q-col-gutter-md">
        <div class="col">
          <q-btn color="primary" label="OK" @click="onOKClick" />
        </div>
        <div class="col text-right">
          <q-btn flat label="Close" v-close-popup />
        </div>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useStore } from "vuex";
import { notify } from "../helpers"

const props = defineProps({
  record: Object
})

const store = useStore();
const rec = ref({ ...props.record })
const show = ref(false)

onMounted(() => {
  show.value = true
  window.onpopstate = function () {
    show.value = false
  }
})
const onOKClick = () => {
  notify({ type: "warning", message: 'Please wait', timeout: 2000, spinner: true })
  store.dispatch('app/deleteRecord', rec)
  show.value = false
}
</script>
