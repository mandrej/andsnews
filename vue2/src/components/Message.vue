<template>
  <v-snackbar left bottom :value="model" :timeout="timeout" @input="close">
    {{ message }}
    <template v-slot:action="{ attrs }">
      <v-btn dark text icon v-bind="attrs" @click="close(false)">
        <v-icon>close</v-icon>
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script>
import { mapState } from 'vuex'
import '@/helpers/fire' // initialized firebase instance
import firebase from 'firebase/app'
import 'firebase/messaging'
import CONFIG from '@/helpers/config'

const messaging = firebase.messaging()

export default {
  name: 'Message',
  data: () => ({
    model: false,
    timeout: 6000,
    message: ''
  }),
  computed: {
    ...mapState('app', ['snackbar'])
  },
  created () {
    window.addEventListener('online', this.updateOnlineStatus)
    window.addEventListener('offline', this.updateOnlineStatus)
  },
  mounted () {
    messaging.onMessage(payload => {
      this.message = payload.notification.body
      if (this.message == CONFIG.end_message) {
        this.timeout = -1
      } else {
        this.timeout = 6000
      }
      this.model = true
    })
  },
  watch: {
    snackbar: function (val) {
      if (val) {
        this.message = val
        this.model = true
      } else {
        this.model = false
      }
    }
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
    }
  }
}
</script>
