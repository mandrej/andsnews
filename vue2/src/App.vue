<template>
  <div id="app">
    <transition name="fade" mode="out-in">
      <router-view></router-view>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: "Roboto", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.area {
  position: relative;
  cursor: pointer;
  background-color: #ddd;
}
.input-file {
  opacity: 0; /* invisible but it's there! */
  width: 100%;
  height: 100%;
  position: absolute;
  cursor: pointer;
}
.v-card__title {
  font-size: 1.25rem !important;
}
.v-toolbar__content > .v-btn.v-btn--icon:first-child + .v-toolbar__title,
.v-toolbar__extension > .v-btn.v-btn--icon:first-child + .v-toolbar__title {
  padding-left: 0;
}
/* transition name="fade" */
.fade-enter-active,
.fade-leave-active {
  transition-duration: 0.3s;
  transition-property: opacity;
  transition-timing-function: ease;
}
.fade-enter,
.fade-leave-active {
  opacity: 0;
}
/* Photoswipe */
.pswp * {
  font-family: "Roboto", Helvetica, Arial, sans-serif !important;
}
.pswp__caption--empty {
  display: block !important;
}
.pswp__caption__center {
  color: #fff !important;
  font-size: 14px !important;
  text-align: center !important;
  opacity: 0.75 !important;
}
</style>
