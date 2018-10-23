<template>
  <div>
    <Add :visible="showAddForm" @close="showAddForm = false"></Add>

    <v-btn v-if="canAdd(user)"
      fab medium fixed bottom right
      color="accent" class="black--text" @click="showAddForm = true">
      <v-icon>add</v-icon>
    </v-btn>

    <v-snackbar
      v-model="snackbar"
      :timeout="timeout"
      left
      bottom>
      {{ text }}
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

    <v-app>
      <v-navigation-drawer v-model="drawer" app fixed floating>
        <v-layout column class="aperture" fill-height>
          <v-toolbar light class="aperture">
            <v-spacer></v-spacer>
            <SignIn></SignIn>
            <v-layout slot="extension" row justify-space-between>
              <v-toolbar-title class="headline">{{total}}</v-toolbar-title>
              <v-toolbar-title class="headline">{{counter()}}</v-toolbar-title>
            </v-layout>
          </v-toolbar>

          <Find class="mt-2" style="background: transparent"></Find>
          <v-spacer></v-spacer>

          <v-list v-if="canAdmin(user)" light style="background: transparent">
            <v-list-tile @click="$router.push({ name: 'admin' })">
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

      <v-toolbar app light class="aperture">
        <v-toolbar-side-icon class="hidden-lg-and-up" @click="drawer = !drawer"></v-toolbar-side-icon>
        <v-spacer></v-spacer>
        <v-toolbar-title class="headline">{{title}}</v-toolbar-title>
        <v-layout slot="extension">
          <v-toolbar-title v-if="filter.value" style="margin-left: -10px">
            <v-btn icon @click="clearFilter">
              <v-icon>close</v-icon>
            </v-btn>
            {{filter.value}}
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <v-progress-circular v-show="busy" :indeterminate="true" color="accent" style="margin-right: 16px"></v-progress-circular>
        </v-layout>
      </v-toolbar>

      <v-content class="aperture" style="background-attachment: fixed">
        <transition name="fade" mode="out-in">
          <component v-bind:is="currentComponent"></component>
        </transition>
      </v-content>

      <Footer :top="true"></Footer>
   </v-app>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import Menu from '@/components/Menu'
import List from '@/components/List'
import Find from '@/components/Find'
import '@/helpers/fire' // local firebase instance
import firebase from 'firebase/app'
import 'firebase/app'
import 'firebase/messaging'

const messaging = firebase.messaging()

export default {
  name: 'Home',
  components: {
    'SignIn': () => import(/* webpackChunkName: "sign-in" */ '@/components/SignIn'),
    'Add': () => import(/* webpackChunkName: "add" */ '@/components/Add'),
    'Footer': () => import(/* webpackChunkName: "footer" */ '@/components/Footer'),
    Menu,
    List,
    Find
  },
  data: () => ({
    drawer: null,
    title: 'ANDрејевићи',
    showAddForm: false,
    text: '',
    snackbar: false,
    timeout: 6000,
    empty: false,
    currentComponent: Menu,
    displayCount: 0,
    interval: false
  }),
  created () {
    this.$store.dispatch('auth/fetchToken')
    const qs = this.$route.params.qs || null
    this.switchComponent(qs)
  },
  mounted () {
    messaging.onMessage(payload => {
      this.text = payload.notification.body
      this.snackbar = true
    })
    this.displayCount = this.count
  },
  watch: {
    count (val) {
      if (val === 0) {
        this.empty = true
      }
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
    '$route.params.qs': {
      handler: 'switchComponent',
      immediate: true
    }
  },
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('app', ['busy', 'filter', 'count', 'total', 'error'])
  },
  methods: {
    canAdd (user) {
      return user && user.isAuthorized
    },
    canAdmin (user) {
      return user && user.isAdmin
    },
    clearFilter () {
      this.$router.push({ name: 'home' })
    },
    switchComponent (qs) {
      if (qs) {
        this.$store.dispatch('app/changeFilter', {
          field: 'search',
          value: qs
        })
        this.$store.dispatch('app/fetchRecords')
        this.currentComponent = List
      } else {
        this.$store.dispatch('app/changeFilter', {})
        this.$store.dispatch('app/fetchMenu')
        this.currentComponent = Menu
      }
    },
    counter () {
      if (this.currentComponent === List) {
        return this.displayCount
      }
    }
  }
}
</script>
