<template>
  <v-snackbar left bottom :value="model" :timeout="timeout" @input="close">
    {{ message }}
    <v-btn dark text icon @click="close(false)">
      <v-icon>close</v-icon>
    </v-btn>
  </v-snackbar>
</template>

<script>
import { EventBus } from '@/helpers/event-bus'
import '@/helpers/fire' // initialized firebase instance
import firebase from '@firebase/app'
import '@firebase/messaging'
import CONFIG from '@/helpers/config'

const messaging = firebase.messaging()

export default {
  name: 'Message',
  data: () => ({
    model: false,
    timeout: 6000,
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
      if (this.message == CONFIG.end_message) {
        this.timeout = 0
      } else {
        this.timeout = 6000
      }
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
      this.timeout = 6000
    },
  }
}
</script>
