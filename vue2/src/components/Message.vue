<template>
  <v-snackbar left bottom :value="model" :timeout="timeout" @input="close">
    {{ message }}
    <v-btn text icon color="white" @click="close(false)">
      <v-icon>close</v-icon>
    </v-btn>
  </v-snackbar>
</template>

<script>
import { EventBus } from '@/helpers/event-bus'

export default {
  name: 'Message',
  props: {
    timeout: {
      Type: Number,
      default: 6000
    }
  },
  data: () => ({
    model: false,
    message: ''
  }),
  mounted () {
    EventBus.$on('snackbar', msg => {
      this.message = msg
      this.model = true
    })
    EventBus.$on('update-snackbar', val => {
      this.model = val
    })
  },
  methods: {
    /**
     * update snackbar from parent
     */
    close (val) {
      this.model = val
    }
  }
}
</script>
