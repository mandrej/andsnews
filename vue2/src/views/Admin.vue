<template>
  <div>
    <Message :model="snackbar" :message="message" @update-snackbar="updateSnackbar"></Message>

    <v-app>
      <v-app-bar app light>
        <v-btn icon @click="$router.go(-1)">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <v-img src="/static/img/aperture.svg" max-height="40" max-width="40" class="mr-3"></v-img>
        <v-toolbar-title class="headline">Admin</v-toolbar-title>
      </v-app-bar>

      <v-content>
        <v-container mt-4>
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
          <v-layout
            wrap
            align-center
            v-for="field in Object.keys(values)"
            :key="field"
            class="py-1"
          >
            <v-flex xs9>Rebuild for field {{field}}</v-flex>
            <v-flex xs3 class="text-right">
              <v-btn
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
              <v-btn
                :disabled="canRun(fcm_token)"
                color="error"
                width="100"
                @click="missing"
              >Missing</v-btn>
            </v-flex>
          </v-layout>
        </v-container>
      </v-content>
    </v-app>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import common from '@/helpers/mixins'
import '@/helpers/fire' // initialized firebase instance
import firebase from '@firebase/app'
import '@firebase/messaging'

const messaging = firebase.messaging()
const axios = Vue.axios

export default {
  name: 'Admin',
  components: {
    'Message': () => import(/* webpackChunkName: "message" */ '@/components/Message')
  },
  mixins: [common],
  data: () => ({
    msg: {
      type: String,
      required: true,
      default: 'NEW IMAGES'
    },
    snackbar: false,
    message: '',
    stat: {}
  }),
  created () {
    axios.get('counter/stat')
      .then(response => {
        this.stat = response.data
      })
  },
  mounted () {
    messaging.onMessage(payload => {
      this.message = payload.notification.body
      this.snackbar = true
    })
  },
  computed: {
    ...mapState('auth', ['fcm_token']),
    ...mapState('app', ['values'])
  },
  methods: {
    updateSnackbar (val) {
      this.snackbar = val
    },
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
