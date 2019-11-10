<template>
  <v-snackbar left bottom :value="model" :timeout="timeout" @input="$emit('close')">
    {{ message }}
    <v-btn text icon color="white" @click="$emit('close')">
      <v-icon>close</v-icon>
    </v-btn>
  </v-snackbar>
</template>

<script>
export default {
  name: 'Message',
  props: {
    model: {
      type: Boolean,
      default: false,
      required: true
    }, message: {
      type: String,
      default: 'MESSAGE'
    }, timeout: {
      Type: Number,
      default: 6000
    }
  }
}
</script>
