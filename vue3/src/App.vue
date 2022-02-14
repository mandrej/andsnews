<template>
  <router-view />
</template>
<script>
import { defineComponent, onMounted } from 'vue';
import { getMessaging, onMessage } from 'firebase/messaging'
import { notify } from "./helpers";

export default defineComponent({
  name: 'App',
  setup() {
    const messaging = getMessaging()

    onMounted(() => {
      onMessage(messaging, payload => {
        notify('external', payload.notification.body)
      })
    })
    return {}
  }
})
</script>
