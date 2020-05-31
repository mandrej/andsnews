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
            <v-app-bar-nav-icon dark class="hidden-lg-and-up pa-2" @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
          </div>
        </template>

        <template v-else>
          <v-app-bar app clipped-left>
            <v-app-bar-nav-icon class="hidden-lg-and-up" @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
            <v-toolbar-title
              class="headline"
              @click="($route.name === 'add') ? $router.go(-1) : $router.push({ name: 'home' })"
              style="cursor: pointer; padding-left: 0"
            >ANDрејевићи</v-toolbar-title>

            <v-spacer></v-spacer>
            <v-avatar size="40px" @click="signHandler" style="cursor: pointer">
              <img v-if="photoUrl" :src="photoUrl" />
              <img v-else src="/static/img/Google__G__Logo.svg" />
            </v-avatar>

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
    Message: () => import(/* webpackChunkName: "message" */ '@/components/Message')
  },
  data: () => ({
    drawer: null
  }),
  created () {
    this.$store.dispatch('app/fetchStat')
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
$darker: #333;
$lighter: #eee;
$almost-black: rgba(0, 0, 0, 0.87);
$almost-white: rgba(255, 255, 255, 0.7);

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
.theme--light.v-navigation-drawer {
  background-color: $lighter;
}
.theme--dark.v-navigation-drawer {
  background-color: $darker;
}
.theme--light.v-app-bar.v-toolbar.v-sheet {
  background-color: var(--v-accent-base);
}
.theme--dark.v-app-bar.v-toolbar.v-sheet {
  background-color: var(--v-accent-base);
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
.theme--light.v-card {
  background-color: white;
  color: $almost-black;
}
.theme--dark.v-card {
  background-color: $dark;
  color: $almost-white;
}
.theme--light.v-btn:not(.v-btn--flat):not(.v-btn--text):not(.v-btn--outlined) {
  background-color: var(--v-accent-base);
}
.theme--dark.v-btn:not(.v-btn--flat):not(.v-btn--text):not(.v-btn--outlined) {
  background-color: var(--v-accent-base);
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
  color: white !important;
  font-size: 14px !important;
  text-align: center !important;
  opacity: 0.75 !important;
}
</style>
