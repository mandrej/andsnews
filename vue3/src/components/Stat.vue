<template>
  <q-list class="q-py-sm">
    <q-item v-for="item in list" :key="item.text" v-ripple clickable>
      <q-item-section>
        <q-item-label class="text-h5 text-weight-light">{{
          item.value
        }}</q-item-label>
        <q-item-label class="text-body2">{{ item.text }}</q-item-label>
      </q-item-section>
    </q-item>
  </q-list>
</template>

<script setup>
import { computed } from "vue";
import { useAppStore } from "../stores/app";
import { formatBytes } from "../helpers";

const app = useAppStore();
const values = computed(() => app.values);
const bucket = computed(() => app.bucket);
const list = [
  {
    value: formatBytes(bucket.value.size),
    text: "storage size",
  },
  {
    value: bucket.value.count,
    text: "photographs",
  },
  {
    value: values.value.year.length,
    text: "years",
  },
  {
    value: values.value.tags.length,
    text: "tags",
  },
  {
    value: values.value.model.length,
    text: "cameras",
  },
  {
    value: values.value.lens.length,
    text: "lenses",
  },
  {
    value: values.value.email.length,
    text: "authors",
  },
];
</script>
