<template>
  <q-list class="q-py-sm">
    <q-item v-for="item in list" :key="item.text" clickable v-ripple>
      <q-item-section>
        <q-item-label class="text-h5 text-weight-light">{{ item.value }}</q-item-label>
        <q-item-label class="text-body2">{{ item.text }}</q-item-label>
      </q-item-section>
    </q-item>
  </q-list>
</template>

<script setup>
import { computed } from "vue";
import { useStore } from "vuex";
import { formatBytes } from "../helpers"

const store = useStore();
const values = computed(() => store.state.app.values)
const bucket = computed(() => store.state.app.bucket)
const list = [
  {
    value: formatBytes(bucket.value.size),
    text: 'storage size'
  },
  {
    value: bucket.value.count,
    text: 'photographs'
  },
  {
    value: values.value.year.length,
    text: 'years'
  },
  {
    value: values.value.tags.length,
    text: 'tags'
  },
  {
    value: values.value.model.length,
    text: 'cameras'
  },
  {
    value: values.value.lens.length,
    text: 'lenses'
  },
  {
    value: values.value.email.length,
    text: 'authors'
  }
]
</script>


