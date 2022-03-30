<template>
  <router-view />
</template>
<script setup>
import { onMounted } from 'vue';
import { useAppStore } from "./store/app";
import { getMessaging, onMessage } from 'firebase/messaging'
import { notify } from "./helpers";

const messaging = getMessaging()
const app = useAppStore()

onMounted(() => {
  app.fetchStat();
  onMessage(messaging, payload => {
    notify({ type: 'ongoing', message: payload.notification.body })
  })
})
</script>
