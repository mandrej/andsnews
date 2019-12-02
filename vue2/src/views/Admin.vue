<template>
  <Layout>
    <template v-slot:drawer="slotProps">
      <v-navigation-drawer v-model="drawer" app fixed clipped width="300" color="accent">
        <v-layout column fill-height>
          <v-list>
            <v-list-item>
              <v-list-item-content>{{total}} photographs</v-list-item-content>
            </v-list-item>
          </v-list>
          <v-spacer></v-spacer>
          <Menu :authorized="slotProps.user.isAuthorized" :admin="slotProps.user.isAdmin"></Menu>
        </v-layout>
      </v-navigation-drawer>
    </template>

    <template v-slot:appbar>
      <v-app-bar app light clipped-left>
        <v-app-bar-nav-icon class="hidden-lg-and-up" @click="drawer = !drawer"></v-app-bar-nav-icon>
        <v-avatar size="40px" @click="$router.push({ name: 'home' })" style="cursor: pointer">
          <v-img src="/static/img/aperture.svg" class="mr-3"></v-img>
        </v-avatar>
        <v-toolbar-title class="headline">Admin</v-toolbar-title>
      </v-app-bar>
    </template>

    <v-container mt-1>
      <h3 class="title">Messaging</h3>
      <v-layout align-center>
        <v-flex xs9>
          <v-text-field
            label="Send message"
            hint="Send message to subscribers group"
            v-model="msg.default"
            type="text"
            @input="upper($event)"
            :rules="requiredRule"
            required
          ></v-text-field>
        </v-flex>
        <v-flex xs3 class="text-right">
          <v-btn color="info" width="100" @click="send">Send</v-btn>
        </v-flex>
      </v-layout>

      <h3 class="title">Counters</h3>
      <v-layout wrap align-center v-for="field in Object.keys(values)" :key="field" class="py-1">
        <v-flex xs9>Rebuild for field {{field}}</v-flex>
        <v-flex xs3 class="text-right">
          <v-btn
            light
            :disabled="canRun(fcm_token)"
            color="primary"
            width="100"
            @click="rebuild(field)"
          >Rebuild</v-btn>
        </v-flex>
      </v-layout>

      <!-- <v-layout wrap align-center>
            <v-flex xs9>Add new fields, remove index docs</v-flex>
            <v-flex xs3 class="text-right">
              <v-btn :disabled="canRun(fcm_token)" color="accent" width="100" class="black--text" @click="fix">Fix</v-btn>
            </v-flex>
      </v-layout>-->

      <h3 class="title">Cloud</h3>
      <v-layout wrap class="py-1" align-center>
        <v-flex xs9>Remove images from the Cloud not referenced in datastore</v-flex>
        <v-flex xs3 class="text-right">
          <v-btn :disabled="canRun(fcm_token)" color="error" width="100" @click="unbound">Remove</v-btn>
        </v-flex>
      </v-layout>
      <v-layout wrap class="py-1" align-center>
        <v-flex xs9>Remove images in datastore that are missing in the Cloud</v-flex>
        <v-flex xs3 class="text-right">
          <v-btn :disabled="canRun(fcm_token)" color="error" width="100" @click="missing">Missing</v-btn>
        </v-flex>
      </v-layout>
    </v-container>
  </Layout>
</template>

<script>
import Vue from 'vue'
import Layout from '@/components/Layout'
import Menu from '@/components/Menu'
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Admin',
  components: {
    Layout,
    Menu
  },
  mixins: [common],
  data: () => ({
    drawer: null,
    msg: {
      type: String,
      required: true,
      default: 'NEW IMAGES'
    }
  }),
  computed: {
    ...mapState('auth', ['fcm_token']),
    ...mapState('app', ['values', 'total'])
  },
  methods: {
    canRun (token) {
      return Boolean(!token)
    },
    callAjax (url) {
      Vue.axios.post(url, { token: this.fcm_token })
        .then(x => x.data)
      // .catch(err => console.log(err))
    },
    rebuild (name) {
      this.callAjax('rebuild/' + name)
    },
    reindex () {
      this.callAjax('reindex')
    },
    unbound () {
      this.callAjax('unbound')
    },
    missing () {
      this.callAjax('missing')
    },
    fix () {
      this.callAjax('fix')
    },
    upper (event) {
      this.msg.default = event.toUpperCase()
    },
    send () {
      this.$store.dispatch('auth/sendNotifications', this.msg.default)
    }
  }
}
</script>
