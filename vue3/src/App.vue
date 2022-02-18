<template>
  <router-view />
</template>
<script>
import { defineComponent, onMounted } from 'vue';
import { useStore } from "vuex";
import { getMessaging, onMessage } from 'firebase/messaging'
import { notify } from "./helpers";

export default defineComponent({
  name: 'App',
  setup() {
    const store = useStore();
    const messaging = getMessaging()

    onMounted(() => {
      store.dispatch("app/fetchStat");
      onMessage(messaging, payload => {
        notify('external', payload.notification.body)
      })
    })
    return {}
  }
})
</script>
