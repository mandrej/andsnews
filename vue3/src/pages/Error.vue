<template>
  <div class="row justify-center text-center q-pa-xl">
    <q-banner rounded class="text-white bg-negative">
      <div class="text-h1">{{ props.code }}</div>
      <div>{{ text }}</div>
      <q-btn flat color="white" size="lg" to="/">
        <q-icon left name="home" />
        <div>Go Home</div>
      </q-btn>
    </q-banner>
  </div>
</template>

<script setup>
import { ref } from "vue";
// eslint-disable-next-line no-undef
const props = defineProps({
  code: {
    type: Number,
    default: 404
  }
})
const errors = {
  404: "Oops. Nothing here...",
  401: "Insufficient credentials..."
}
const text = ref(errors[props.code])

</script>
