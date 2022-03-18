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

<style>
/* 1. declare transition */
.fade-move,
.fade-enter-active,
.fade-leave-active {
  transition: all 0.5s cubic-bezier(0.55, 0, 0.1, 1);
}
/* 2. declare enter from and leave to state */
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scaleY(0.3) translate(30px, 0);
}
/* 3. ensure leaving items are taken out of layout flow so that moving
      animations can be calculated correctly. */
.fade-leave-active {
  position: absolute;
}

/** bounce effect */
@keyframes bounce {
  0%,
  20%,
  50%,
  80%,
  100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-30px);
  }
  60% {
    transform: translateY(-15px);
  }
}
.bounce {
  animation-name: bounce;
  animation-duration: 1s;
  animation-fill-mode: both;
}
</style>
