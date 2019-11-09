<template>
  <v-snackbar left bottom v-model="snackbarModel" :timeout="snackbarTimeout">
    {{ message }}
    <v-btn text icon color="white" @click="snackbarModel = false">
      <v-icon>close</v-icon>
    </v-btn>
  </v-snackbar>
</template>

<script>
export default {
  name: 'Message',
  props: ['model', 'message', 'timeout'],
  computed: {
    snackbarModel () {
      return this.model
    },
    snackbarTimeout () {
      return (this.timeout) ? this.timeout : 6000
    }
  }
}
</script>
