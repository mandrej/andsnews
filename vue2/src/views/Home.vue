<template>
  <div>
    <Add :visible="showAddForm" @close="showAddForm = false"></Add>

    <v-btn v-if="isAuthorized"
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
        <v-card-title class="headline warning" primary-title>
          No photos
        </v-card-title>
        <v-card-text>
          for current filter / search
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-3">
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="empty = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-app>
      <v-navigation-drawer v-model="drawer" app fixed>
        <v-layout column class="aperture" fill-height>
          <v-toolbar dark class="aperture" color="secondary">
            <v-spacer></v-spacer>
            <SignIn></SignIn>
            <v-layout slot="extension">
              <v-toolbar-title style="font-size: 32px">{{count}}/{{total}}</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-layout>
          </v-toolbar>

          <Find class="mt-2" style="background: transparent"></Find>
          <v-spacer></v-spacer>

          <v-list light>
            <v-list-tile @click="$router.push({name: 'admin'})">
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

      <v-toolbar app light class="aperture" color="white">
        <v-toolbar-side-icon class="hidden-lg-and-up" @click="drawer = !drawer"></v-toolbar-side-icon>
        <v-spacer></v-spacer>
        <v-layout slot="extension">
          <v-toolbar-title v-if="filter.value" style="margin-left: -10px">
            <v-btn icon @click="clearFilter">
              <v-icon>close</v-icon>
            </v-btn>
            {{formatFilter(filter.value)}}
          </v-toolbar-title>
          <v-toolbar-title v-else style="font-size: 32px">{{title}}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-progress-circular v-show="busy" :indeterminate="true" color="accent" style="margin-right: 16px"></v-progress-circular>
        </v-layout>
      </v-toolbar>

      <v-content class="aperture" style="background-attachment: fixed">
        <List></List>
      </v-content>

      <Footer :top="true"></Footer>
   </v-app>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import List from '@/components/List'
import Find from '@/components/Find'
import { EventBus } from '@/helpers/event-bus'
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
    isAuthorized: null
  }),
  created () {
    this.$store.dispatch('All/fetchInfo')
    this.$store.dispatch('All/fetchToken')
  },
  mounted () {
    if (this.user && this.user.isAuthorized) {
      this.isAuthorized = this.user.isAuthorized
    }
    EventBus.$on('signin', user => {
      if (user && user.isAuthorized) {
        this.isAuthorized = user.isAuthorized
      } else {
        this.isAuthorized = null
      }
    })
    messaging.onMessage(payload => {
      this.text = payload.notification.body
      this.snackbar = true
    })
  },
  watch: {
    count (val) {
      if (val === 0) {
        this.empty = true
      }
    }
  },
  computed: {
    ...mapState('All', ['user', 'busy', 'filter', 'count', 'total'])
  },
  methods: {
    formatFilter(filter) {
      const result = filter.match(/".+?"/g)
      return result.join(' AND ')
    },
    clearFilter () {
      this.$store.dispatch('All/changeFilter', {})
    }
  }
}
</script>
