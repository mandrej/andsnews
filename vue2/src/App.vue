<template>
  <div id="app">
    <Message>></Message>
    <transition name="fade" mode="out-in">
      <v-app>
        <v-navigation-drawer v-model="drawer" app fixed clipped :width="300">
          <v-layout column fill-height>
            <keep-alive>
              <component :is="dynamicComponent"></component>
            </keep-alive>
            <v-spacer></v-spacer>
            <Menu></Menu>
          </v-layout>
        </v-navigation-drawer>

        <template v-if="$route.name === 'home'">
          <div class="hamburger">
            <v-app-bar-nav-icon dark class="hidden-lg-and-up pa-2" @click="drawer = !drawer"></v-app-bar-nav-icon>
          </div>
        </template>

        <template v-else>
          <v-app-bar app clipped-left>
            <v-app-bar-nav-icon class="hidden-lg-and-up" @click="drawer = !drawer"></v-app-bar-nav-icon>
            <v-toolbar-title
              class="headline"
              @click="($route.name === 'add') ? $router.go(-1) : $router.push({ name: 'home' })"
              style="cursor: pointer; padding-left: 0"
            >ANDрејевићи</v-toolbar-title>
            <v-spacer></v-spacer>
            <SignIn></SignIn>
            <v-progress-linear v-show="busy" absolute top color="accent" :indeterminate="true"></v-progress-linear>
          </v-app-bar>
        </template>

        <v-content>
          <router-view></router-view>
        </v-content>
      </v-app>
    </transition>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import Menu from '@/components/Menu'
import Find from '@/components/Find'
import Stat from '@/components/Stat'
import VueLazyload from 'vue-lazyload'

Vue.use(VueLazyload, {
  attempt: 1,
  error: '/static/img/broken.svg'
})

export default {
  name: 'App',
  components: {
    Menu,
    Find,
    Stat: () => import(/* webpackChunkName: "stat" */ '@/components/Stat'),
    SignIn: () => import(/* webpackChunkName: "sign-in" */ '@/components/SignIn'),
    Message: () => import(/* webpackChunkName: "message" */ '@/components/Message')
  },
  data: () => ({
    drawer: null
  }),
  created () {
    this.$store.dispatch('app/fetchStat')
  },
  computed: {
    ...mapState('app', ['busy']),
    dynamicComponent () {
      switch (this.$route.name) {
        case 'home':
        case 'list':
          return Find
        default:
          return Stat
      }
    }
  }
}
</script>

<style>
#app {
  font-family: "Roboto", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.hamburger {
  position: absolute;
  top: 0;
  left: 0;
  padding: 6px;
  z-index: 2;
}
.theme--light.v-app-bar.v-toolbar.v-sheet {
  background-color: #fff;
}
.area {
  position: relative;
  cursor: pointer;
  background-color: rgba(0, 0, 0, 0.05);
}
.input-file {
  opacity: 0; /* invisible but it's there! */
  width: 100%;
  height: 100%;
  position: absolute;
  cursor: pointer;
}
.v-card__title {
  line-height: 120%;
  font-size: 1.25rem !important;
}
.v-dialog > .v-card > .v-card__text {
  padding: 0 20px 20px;
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
/* Lazy image */
img.lazy {
  opacity: 0;
  display: block;
  width: 100%;
  height: 250px;
  object-fit: cover;
  transition: opacity 0.3s;
  cursor: pointer;
}
img.lazy[lazy="loaded"],
img.lazy[lazy="error"] {
  opacity: 1;
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
