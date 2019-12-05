<template>
  <div>
    <Message>></Message>
    <v-app>
      <slot name="drawer"></slot>
      <slot name="appbar"></slot>
      <v-content class="accent">
        <slot></slot>
      </v-content>
    </v-app>
  </div>
</template>

<script>
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
  mounted () {
    messaging.onMessage(payload => {
      EventBus.$emit('snackbar', payload.notification.body)
    })

    window.addEventListener('online', this.updateOnlineStatus)
    window.addEventListener('offline', this.updateOnlineStatus)
  },
  methods: {
    updateOnlineStatus (event) {
      EventBus.$emit('snackbar', 'You are ' + event.type)
    }
  }
}
</script>

