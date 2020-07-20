<template>
  <div id="app">
    <Message>></Message>
    <transition name="fade" mode="out-in">
      <v-app>
        <v-navigation-drawer
          v-model="drawer"
          app
          fixed
          floating
          clipped
          color="secondary"
          :width="300"
        >
          <v-layout column fill-height>
            <keep-alive>
              <component :is="dynamicComponent"></component>
            </keep-alive>
            <v-spacer></v-spacer>
            <Menu></Menu>
          </v-layout>
        </v-navigation-drawer>

        <v-app-bar app clipped-left flat color="accent">
          <v-app-bar-nav-icon class="hidden-lg-and-up" @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
          <v-toolbar-title
            class="headline"
            @click="($route.name === 'add') ? $router.go(-1) : $router.push({ name: 'home' })"
            style="cursor: pointer; padding-left: 0"
          >ANDрејевићи</v-toolbar-title>

          <v-spacer></v-spacer>
          <v-avatar size="40px" @click="signHandler" style="cursor: pointer">
            <img v-if="photoUrl" :src="photoUrl" />
            <img v-else src="/static/Google__G__Logo.svg" />
          </v-avatar>

          <v-progress-linear v-show="busy" absolute top color="primary" :indeterminate="true"></v-progress-linear>
        </v-app-bar>

        <v-main>
          <router-view></router-view>
        </v-main>
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
import CONFIG from '@/helpers/config'

Vue.use(VueLazyload, {
  attempt: 1,
  observer: true,
  error: CONFIG.fileBroken
})

export default {
  name: 'App',
  components: {
    Menu,
    Find,
    Stat: () => import(/* webpackChunkName: "stat" */ '@/components/Stat'),
    Message: () => import(/* webpackChunkName: "message" */ '@/components/Message')
  },
  data: () => ({
    drawer: null
  }),
  created () {
    this.$store.dispatch('app/fetchStat')
    this.$store.dispatch('app/bucketInfo', { verb: 'get' })
    this.$vuetify.theme.dark = this.dark
  },
  computed: {
    ...mapState('app', ['busy', 'dark']),
    ...mapState('auth', ['user']),
    photoUrl () {
      return this.user && this.user.photo
    },
    dynamicComponent () {
      switch (this.$route.name) {
        case 'home':
        case 'list':
          return Find
        default:
          return Stat
      }
    }
  },
  methods: {
    signHandler () {
      this.$store.dispatch('auth/signIn')
    }
  }
}
</script>

<style lang="scss">
$dark: #444;
$darker: #2e2e2e;
$lighter: #efefef;
$almost-black: rgba(0, 0, 0, 0.87);
$almost-white: rgba(255, 255, 255, 0.87);

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
.theme--light.v-application {
  background: white;
  color: $almost-black;
}
.theme--dark.v-application {
  background: $dark;
  color: $almost-white;
}
.theme--light.v-sheet {
  background-color: $lighter;
  border-color: $lighter;
  color: $almost-black;
}
.theme--dark.v-sheet {
  background-color: $darker;
  border-color: $darker;
  color: $almost-white;
}
.v-card__title {
  line-height: 125%;
}
.input-file {
  opacity: 0; /* invisible but it's there! */
  width: 100%;
  height: 100%;
  position: absolute;
  cursor: pointer;
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
  color: white !important;
  font-size: 14px !important;
  text-align: center !important;
  opacity: 0.75 !important;
}
</style>
