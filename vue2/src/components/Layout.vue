<template>
  <div>
    <Message :model="snackbar" :message="message" @update-snackbar="updateSnackbar"></Message>

    <v-app>
      <slot name="drawer" v-bind:user="user"></slot>
      <slot name="appbar"></slot>
      <v-content class="accent">
        <slot></slot>
      </v-content>
    </v-app>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { EventBus } from '@/helpers/event-bus'
import '@/helpers/fire' // initialized firebase instance
import firebase from '@firebase/app'
import '@firebase/messaging'

const messaging = firebase.messaging()

export default {
  name: 'Layout',
  components: {
    'Message': () => import(/* webpackChunkName: "message" */ '@/components/Message')
  },
  data: () => ({
    snackbar: false,
    message: ''
  }),
  mounted () {
    EventBus.$on('snackbar', msg => {
      this.message = msg
      this.snackbar = true
    })

    messaging.onMessage(payload => {
      this.message = payload.notification.body
      this.snackbar = true
    })

    window.addEventListener('online', this.updateOnlineStatus)
    window.addEventListener('offline', this.updateOnlineStatus)
  },
  computed: {
    ...mapState('auth', ['user']),
  },
  methods: {
    updateOnlineStatus (event) {
      EventBus.$emit('snackbar', 'You are ' + event.type)
    },
    updateSnackbar (val) {
      // <Message :model="snackbar" :message="message" @update-snackbar="updateSnackbar"></Message>
      this.snackbar = val
    }
  }
}
</script>

