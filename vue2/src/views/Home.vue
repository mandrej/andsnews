<template>
  <div>
    <v-snackbar left bottom
      v-model="snackbar"
      :timeout="timeout">
      {{ message }}
      <v-btn flat icon color="white" @click="snackbar = false">
        <v-icon>close</v-icon>
      </v-btn>
    </v-snackbar>

    <v-dialog v-model="empty" max-width="300px" lazy>
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
        <v-layout column class="aperture" fill-height>
          <v-toolbar light class="aperture">
            <v-spacer></v-spacer>
            <span v-if="isAuthorized" style="padding-right: 1em">{{user.name}}</span>
            <span v-else style="padding-right: 1em">sign-in</span>
            <SignIn></SignIn>
            <v-layout slot="extension" justify-end row>
              <v-toolbar-title class="subheading">{{counter()}}</v-toolbar-title>
            </v-layout>
          </v-toolbar>

          <Find class="mt-2" style="background: transparent"></Find>
          <v-spacer></v-spacer>

          <v-list light style="background: transparent">
            <v-list-tile v-if="isAdmin" @click="$router.push({ name: 'admin' })">
              <v-list-tile-action>
                <v-icon>settings</v-icon>
              </v-list-tile-action>
              <v-list-tile-content>
                <v-list-tile-title>Admin</v-list-tile-title>
              </v-list-tile-content>
            </v-list-tile>
          </v-list>
        </v-layout>
      </v-navigation-drawer>

      <v-toolbar v-if="filter.value" app light class="aperture">
        <v-toolbar-side-icon class="hidden-lg-and-up" @click="drawer = !drawer"></v-toolbar-side-icon>
        <v-spacer></v-spacer>
        <v-toolbar-title class="headline font-weight-light">{{title}}</v-toolbar-title>
        <v-layout slot="extension">
          <v-toolbar-title style="margin-left: -10px">
            <v-btn icon @click="clearFilter">
              <v-icon>close</v-icon>
            </v-btn>
            {{filter.value}}
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <v-progress-circular v-show="busy" color="secondary" :indeterminate="true" style="margin-right: 16px"></v-progress-circular>
        </v-layout>
      </v-toolbar>
      <div v-else style="position: absolute; top: 0; left: 0; z-index: 2">
        <v-toolbar-side-icon dark class="hidden-lg-and-up pa-2" @click="drawer = !drawer"></v-toolbar-side-icon>
      </div>

      <v-content class="aperture" style="background-attachment: fixed">
        <transition name="fade" mode="out-in">
          <component v-bind:is="currentComponent"></component>
        </transition>
      </v-content>

      <v-footer height="auto" app inset>
        <v-layout>
          <v-spacer></v-spacer>
           <v-btn fab flat small @click="$vuetify.goTo(0, options)">
            <v-icon>arrow_upward</v-icon>
          </v-btn>
          <v-spacer></v-spacer>
        </v-layout>
      </v-footer>
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
import firebase from 'firebase/app'
import 'firebase/messaging'
import * as easings from 'vuetify/es5/components/Vuetify/goTo/easing-patterns'

const messaging = firebase.messaging()

export default {
  name: 'Home',
  components: {
    'SignIn': () => import(/* webpackChunkName: "sign-in" */ '@/components/SignIn'),
    Menu,
    List,
    Find
  },
  props: ['qs'],
  data: () => ({
    isAdmin: false,
    isAuthorized: false,
    drawer: null,
    title: 'ANDрејевићи',
    empty: false,
    currentComponent: Menu,
    displayCount: 0,
    interval: false,
    options: {
      duration: 300,
      offset: 0,
      easings: Object.keys(easings)
    },
    snackbar: false,
    timeout: 6000,
    message: ''
  }),
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
    this.displayCount = this.count
  },
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('app', ['busy', 'filter', 'count', 'total', 'error']),
    version () {
      return process.env.VUE_APP_VERSION.match(/.{1,4}/g).join('.')
    }
  },
  watch: {
    count: function (val) {
      this.empty = val === 0
      // https://stackoverflow.com/questions/35531629/vuejs-animate-number-changes
      clearInterval(this.interval)
      this.interval = setInterval(() => {
        if (this.displayCount !== val) {
          let change = (val - this.displayCount) / 10
          change = change >= 0 ? Math.ceil(change) : Math.floor(change)
          this.displayCount += change
        }
      }, 20)
    },
    qs: {
      handler: function (val) {
        if (val) {
          this.$store.dispatch('app/changeFilter', {
            field: 'search',
            value: val
          })
          this.$store.dispatch('app/fetchRecords')
          this.currentComponent = List
        } else {
          this.$store.dispatch('app/changeFilter', {})
          this.$store.dispatch('app/fetchMenu')
          this.currentComponent = Menu
        }
      },
      immediate: true
    }
  },
  methods: {
    updateOnlineStatus (event) {
      EventBus.$emit('status', 'You are ' + event.type)
    },
    clearFilter () {
      this.$router.push({ name: 'home' })
    },
    counter () {
      if (this.currentComponent === List) {
        return this.displayCount + '/' + this.total
      } else {
        return '2007-' + this.version
      }
    },
    onResize () {
      EventBus.$emit('resize')
    }
  }
}
</script>
