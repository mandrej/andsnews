<template>
  <div id="app">
    <Message>></Message>

    <v-snackbar left bottom :value="updateExists" :timeout="-1">
      An update is available
      <template v-slot:action="{ attrs }">
        <v-btn dark text v-bind="attrs" @click="refreshApp" style="margin: 0 8px">Update</v-btn>
      </template>
    </v-snackbar>

    <v-app>
      <v-navigation-drawer v-model="drawer" app fixed floating clipped :width="300">
        <div class="d-flex flex-column fill-height">
          <keep-alive>
            <component :is="dynamicComponent"></component>
          </keep-alive>
          <v-spacer></v-spacer>
          <Menu></Menu>
        </div>
      </v-navigation-drawer>

      <v-app-bar app clipped-left>
        <v-app-bar-nav-icon class="hidden-lg-and-up" @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
        <v-toolbar-title
          class="text-h5"
          @click="goBack"
          style="cursor: pointer; padding-left: 0"
        >{{title}}</v-toolbar-title>

        <v-progress-linear v-show="busy" color="secondary" absolute top :indeterminate="true"></v-progress-linear>
      </v-app-bar>

      <v-main>
        <router-view></router-view>
      </v-main>
    </v-app>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import Menu from '@/components/Menu'
import Find from '@/components/Find'
import Stat from '@/components/Stat'
import VueLazyload from 'vue-lazyload'
import update from '@/helpers/update'
import CONFIG from '@/helpers/config'

Vue.use(VueLazyload, {
  observer: true,
  error: CONFIG.fileBroken
})

export default {
  name: 'App',
  mixins: [update],
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
    this.$store.dispatch('auth/getPermission')
    this.$vuetify.theme.dark = this.dark
    // Session life time 7 days
    if (this.user && this.user.lastLogin) {
      if (Date.now() - this.user.lastLogin > CONFIG.lifeTime) { // millis
        this.$store.dispatch('auth/signIn')
      }
    }
  },
  computed: {
    ...mapState('app', ['busy', 'dark']),
    ...mapState('auth', ['user']),
    title () {
      return this.$route.meta.title || 'ANDрејевићи'
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
    goBack () {
      if (this.$route.name === 'add') {
        this.$router.go(-1)
      } else {
        this.$router.push({ name: 'home' })
      }
    }
  }
}
</script>

<style lang="scss">
#app {
  font-family: "Roboto", Helvetica, Arial, sans-serif;
}
.v-application {
  background-color: var(--v-background-base) !important;
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
.theme--light path {
  fill: white;
  fill-opacity: 0.5;
}
.theme--dark path {
  fill: black;
  fill-opacity: 0.5;
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
/* Lazy image */
.lazy {
  position: absolute;
  opacity: 0;
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s;
}
.lazy[lazy="loaded"],
.lazy[lazy="error"] {
  opacity: 1;
}
img.lazy + p {
  position: absolute;
  bottom: 0;
  color: white;
  margin: 0;
  padding: 16px;
  line-height: 120% !important;
}
</style>
