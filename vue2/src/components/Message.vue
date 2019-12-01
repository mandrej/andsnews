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
  },
  mounted () {
    EventBus.$on('update-snackbar', val => {
      this.close(val)
    })
  },
  methods: {
    close (val) {
      // <Message :model="snackbar" :message="message" @update-snackbar="updateSnackbar"></Message>
      this.$emit('update-snackbar', val)
    }
  }
}
</script>
