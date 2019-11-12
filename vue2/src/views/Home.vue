<template>
  <div>
    <Message :model="snackbar" :message="message" @update-snackbar="updateSnackbar"></Message>

    <v-app v-resize="onResize">
      <v-navigation-drawer v-model="drawer" app fixed clipped width="300" color="accent">
        <v-layout column fill-height>
          <Find></Find>
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

      <v-app-bar v-if="!isFront" app light clipped-left>
        <v-app-bar-nav-icon class="hidden-lg-and-up" @click="drawer = !drawer"></v-app-bar-nav-icon>
        <v-img src="/static/img/aperture.svg" max-height="40" max-width="40" class="mr-3"></v-img>
        <v-toolbar-title class="headline font-weight-regular">ANDрејевићи</v-toolbar-title>
        <v-spacer></v-spacer>
        <SignIn></SignIn>
        <v-progress-linear v-show="busy" absolute top color="accent" :indeterminate="true"></v-progress-linear>
      </v-app-bar>
      <div v-else class="front">
        <v-app-bar-nav-icon dark class="hidden-lg-and-up pa-2" @click="drawer = !drawer"></v-app-bar-nav-icon>
      </div>

      <v-content>
        <transition name="fade" mode="out-in">
          <component :is="currentComponent"></component>
        </transition>
      </v-content>
    </v-app>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import Front from '@/components/Front'
import List from '@/components/List'
import Find from '@/components/Find'
import { EventBus } from '@/helpers/event-bus'
import common from '@/helpers/mixins'
import '@/helpers/fire' // initialized firebase instance
import firebase from '@firebase/app'
import '@firebase/messaging'

const messaging = firebase.messaging()

export default {
  name: 'Home',
  components: {
    'SignIn': () => import(/* webpackChunkName: "sign-in" */ '@/components/SignIn'),
    'Message': () => import(/* webpackChunkName: "message" */ '@/components/Message'),
    Front,
    List,
    Find
  },
  mixins: [common],
  data: () => ({
    isAdmin: false,
    isAuthorized: false,
    drawer: null,
    empty: false,
    currentComponent: Front,
    snackbar: false,
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
  },
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('app', ['busy']),
    isFront () {
      return this.currentComponent === Front
    },
    version () {
      return process.env.VUE_APP_VERSION.match(/.{1,4}/g).join('.')
    }
  },
  watch: {
    '$route.query': {
      immediate: true,
      handler: function (val) {
        const tmp = {}
        Object.keys(val).forEach(key => {
          if (!isNaN(val[key])) {
            tmp[key] = Number(val[key])
          } else if (Array.isArray(val[key])) {
            tmp[key] = [...val[key]]
          } else {
            tmp[key] = val[key]
          }
        })
        this.$store.dispatch('app/saveFindForm', tmp)

        if (Object.keys(tmp).length) {
          this.$store.dispatch('app/changeFilter', { reset: true })
          this.currentComponent = List
        } else {
          this.$store.dispatch('app/changeFilter', { reset: false })
          this.currentComponent = Front
        }
      }
    }
  },
  methods: {
    updateOnlineStatus (event) {
      EventBus.$emit('status', 'You are ' + event.type)
    },
    onResize () {
      EventBus.$emit('resize')
    }
  }
}
</script>

<style scoped>
.front {
  position: absolute;
  top: 0;
  left: 0;
  padding: 6px;
  z-index: 2;
}
</style>
