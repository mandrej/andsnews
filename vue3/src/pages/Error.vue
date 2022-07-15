<template>
  <div class="absolute-center text-center">
    <q-banner rounded class="text-white q-pa-md bg-negative">
      <div class="text-h3">{{ props.code }}</div>
      {{ text }}
      <template v-slot:action>
        <q-btn flat color="white" size="lg" to="/">
          <q-icon left name="home" />
          <div>Go Home</div>
        </q-btn>
      </template>
    </q-banner>
  </div>
</template>

<script setup>
import { ref } from "vue";
// eslint-disable-next-line no-undef
const props = defineProps({
  code: {
    type: [String, Number],
    default: 404,
  },
});
const errors = {
  404: "Oops. Nothing here...",
  401: "Insufficient credentials...",
};
const text = ref(errors[props.code]);
</script>
