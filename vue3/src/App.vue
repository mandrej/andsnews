<template>
  <router-view />
</template>
<script setup>
import { onMounted } from 'vue';
import { useStore } from "vuex";
import { getMessaging, onMessage } from 'firebase/messaging'
import { notify } from "./helpers";

const store = useStore();
const messaging = getMessaging()

onMounted(() => {
  store.dispatch("app/fetchStat");
  onMessage(messaging, payload => {
    notify({ type: 'ongoing', message: payload.notification.body })
  })
})
</script>
