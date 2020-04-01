<template>
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
      <slot></slot>
    </v-content>
  </v-app>
</template>

<script>
import { mapState } from 'vuex'
import Menu from '@/components/Menu'
import Find from '@/components/Find'
import Stat from '@/components/Stat'

export default {
  name: 'Layout',
  components: {
    Menu,
    Find,
    Stat: () => import(/* webpackChunkName: "stat" */ '@/components/Stat'),
    SignIn: () => import(/* webpackChunkName: "sign-in" */ '@/components/SignIn')
  },
  data: () => ({
    drawer: null
  }),
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
