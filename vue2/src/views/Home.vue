<template>
  <div>
    <v-snackbar left bottom
      v-model="snackbar"
      :timeout="timeout">
      {{ message }}
      <v-btn text icon color="white" @click="snackbar = false">
        <v-icon>close</v-icon>
      </v-btn>
    </v-snackbar>

    <v-dialog v-model="empty" max-width="300px">
      <v-card>
        <v-card-title v-if="error" class="headline warning error--text" primary-title>
          Error
        </v-card-title>
        <v-card-title v-else class="headline warning" primary-title>
          No photos
        </v-card-title>
        <v-card-text>
          <template v-if="error">{{error}}</template>
          <template v-else>For current filter | search</template>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-3">
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="empty = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-app v-resize="onResize">
      <v-navigation-drawer v-model="drawer" app fixed floating>
        <v-layout column fill-height class="aperture">
          <v-app-bar flat grow-shrink-0 light style="background: transparent">
            <v-spacer></v-spacer>
            <span v-if="isAuthorized" style="padding-right: 1em">{{user.name}}</span>
            <span v-else style="padding-right: 1em">sign-in</span>
            <SignIn></SignIn>
          </v-app-bar>

          <Find style="background: transparent"></Find>
          <v-spacer></v-spacer>

          <v-list>
            <v-list-item v-if="isAuthorized" @click="$router.push({ name: 'add' })">
              <v-list-item-action>
                <v-icon>add_circle</v-icon>
              </v-list-item-action>
              <v-list-item-content>
                <v-list-item-title>Add</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item v-if="isAdmin" @click="$router.push({ name: 'admin' })">
              <v-list-item-action>
                <v-icon>settings</v-icon>
              </v-list-item-action>
              <v-list-item-content>
                <v-list-item-title>Admin</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content class="caption">© 2007-{{version}}</v-list-item-content>
            </v-list-item>
          </v-list>
        </v-layout>
      </v-navigation-drawer>

      <v-app-bar app flat class="aperture" style="transform: none; /* FF bug */">
        <v-app-bar-nav-icon class="hidden-lg-and-up" @click="drawer = !drawer"></v-app-bar-nav-icon>
        <v-spacer></v-spacer>
        <v-progress-circular v-show="busy" :indeterminate="true" style="margin-right: 16px"></v-progress-circular>
        <v-toolbar-title class="headline font-weight-regular">ANDрејевићи</v-toolbar-title>
      </v-app-bar>

      <v-content class="aperture">
        <transition name="fade" mode="out-in">
          <component v-bind:is="currentComponent"></component>
        </transition>
      </v-content>

      <v-btn fab large fixed bottom right
        color="accent" class="black--text"
        style="bottom: 16px; right: 22px"
        @click="$vuetify.goTo(0, options)">
        <v-icon>arrow_upward</v-icon>
      </v-btn>
   </v-app>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import Menu from '@/components/Menu'
import List from '@/components/List'
import Find from '@/components/Find'
import { EventBus } from '@/helpers/event-bus'
import '@/helpers/fire' // local firebase instance
import firebase from '@firebase/app'
import '@firebase/messaging'
import * as easings from 'vuetify/es5/services/goto/easing-patterns'

const messaging = firebase.messaging()

export default {
  name: 'Home',
  components: {
    'SignIn': () => import(/* webpackChunkName: "sign-in" */ '@/components/SignIn'),
    Menu,
    List,
    Find
  },
  props: ['text', 'tags', 'year', 'month', 'model', 'email'],
  data: () => ({
    isAdmin: false,
    isAuthorized: false,
    drawer: null,
    empty: false,
    currentComponent: Menu,
    options: {
      duration: 300,
      offset: 0,
      easings: Object.keys(easings)
    },
    snackbar: false,
    timeout: 6000,
    message: ''
  }),
  created () {
    this.$store.dispatch('auth/fetchToken')
  },
  mounted () {
    window.addEventListener('online', this.updateOnlineStatus)
    window.addEventListener('offline', this.updateOnlineStatus)
    EventBus.$on('status', msg => {
      this.message = msg
      this.snackbar = true
    })
    this.isAuthorized = this.user && this.user.isAuthorized
    this.isAdmin = this.user && this.user.isAdmin
    EventBus.$on('signin', user => {
      this.isAuthorized = user && user.isAuthorized
      this.isAdmin = user && user.isAdmin
    })
    messaging.onMessage(payload => {
      this.message = payload.notification.body
      this.snackbar = true
    })
  },
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('app', ['busy', 'count', 'error']),
    version () {
      return process.env.VUE_APP_VERSION.match(/.{1,4}/g).join('.')
    }
  },
  watch: {
    count: function (val) {
      this.empty = val === 0
    },
    '$route.query': {
      immediate: true,
      handler: function (val) {
        if (Object.keys(val).length) {
          this.$store.dispatch('app/changeFilter', { reset: true })
          this.currentComponent = List
        } else {
          this.$store.dispatch('app/changeFilter', { reset: false })
          this.currentComponent = Menu
        }
      }
    }
  },
  methods: {
    updateOnlineStatus (event) {
      EventBus.$emit('status', 'You are ' + event.type)
    },
    clearFilter () {
      this.$router.push({ name: 'home' })
    },
    onResize () {
      EventBus.$emit('resize')
    }
  }
}
</script>
