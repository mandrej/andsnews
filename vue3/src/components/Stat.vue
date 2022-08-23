<template>
  <q-list class="q-py-md">
    <q-item>
      <q-item-section>
        <q-item-label class="text-white" overline>SITE STATISTICS</q-item-label>
      </q-item-section>
    </q-item>
    <q-item
      v-for="item in list"
      :key="item.value"
      class="text-h6 text-warning text-weight-light"
      clickable
    >
      <q-item-section>
        {{ item.value }}
      </q-item-section>
      <q-item-section side>
        {{ item.text }}
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
const list = computed(() => [
  {
    text: "storage",
    value: formatBytes(bucket.value.size),
  },
  {
    text: "photographs",
    value: bucket.value.count,
  },
  {
    text: "years",
    value: values.value.year.length,
  },
  {
    text: "tags",
    value: values.value.tags.length,
  },
  {
    text: "cameras",
    value: values.value.model.length,
  },
  {
    text: "lenses",
    value: values.value.lens.length,
  },
  {
    text: "authors",
    value: values.value.email.length,
  },
]);
</script>
