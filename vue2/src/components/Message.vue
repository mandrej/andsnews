<template>
  <v-snackbar left bottom :value="model" :timeout="timeout" @input="close">
    {{ message }}
    <template v-slot:action="{ attrs }">
      <v-btn dark text icon v-bind="attrs" @click="close(false)">
        <v-icon>{{mdiClose}}</v-icon>
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script>
import { mapState } from 'vuex'
import { getMessaging, onMessage } from 'firebase/messaging'
import common from '../helpers/mixins'
import CONFIG from '../helpers/config'

const messaging = getMessaging()

export default {
  name: 'Message',
  mixins: [common],
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
    onMessage(messaging, payload => {
      this.message = payload.notification.body
      if (this.message.startsWith(CONFIG.end_message)) {
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
