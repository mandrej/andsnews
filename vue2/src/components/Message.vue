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
import '@/helpers/fire' // initialized firebase instance
import firebase from '@firebase/app'
import '@firebase/messaging'

const messaging = firebase.messaging()

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
      // update snackbar from ouside
      this.model = val
    })
    messaging.onMessage(payload => {
      this.message = payload.notification.body
      this.model = true
    })
    window.addEventListener('online', this.updateOnlineStatus)
    window.addEventListener('offline', this.updateOnlineStatus)
  },
  methods: {
    updateOnlineStatus (event) {
      this.message = 'You are ' + event.type
      this.model = true
    },
    close (val) {
      // update snackbar from inside
      this.model = val
    },
  }
}
</script>
