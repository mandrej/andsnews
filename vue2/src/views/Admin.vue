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

    <v-app>
      <v-app-bar app flat light class="aperture">
        <v-btn icon @click="$router.push({ name: 'home' })">
          <v-icon>home</v-icon>
        </v-btn>
        <v-toolbar-title class="headline">Admin</v-toolbar-title>
      </v-app-bar>

      <v-content class="aperture">
        <v-container mt-4>
          <v-layout row align-center>
            <v-flex xs12>
              <h3 class="title">Messaging</h3>
            </v-flex>
            <v-flex xs9>
              <v-text-field
                label="Send message"
                hint="Send message to subscribers group"
                v-model="msg.default"
                type="text"
                @input="upper($event)"
                :rules="requiredRule"
                required></v-text-field>
            </v-flex>
            <v-flex xs3 class="text-right">
              <v-btn color="secondary" @click="send">Send</v-btn>
            </v-flex>
          </v-layout>

          <v-layout row align-center class="py-1">
            <v-flex xs12>
              <h3 class="title">Counters</h3>
            </v-flex>
          </v-layout>
          <v-layout row align-center v-for="field in Object.keys(values)" :key="field" class="py-1">
            <v-flex xs9>Rebuild for field {{field}}</v-flex>
            <v-flex xs3 class="text-right">
              <v-btn :disabled="canRun(fcm_token)" color="secondary" @click="rebuild(field)">Rebuild</v-btn>
            </v-flex>
            <v-flex xs12 class="py-3 hidden-sm-and-down">
              <v-simple-table dense>
                <thead>
                  <tr>
                    <th class="text-left">Name</th>
                    <th class="text-right">Count</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in stat[field]" :key="item.value">
                    <td>{{ item.value }}</td>
                    <td class="text-right">{{ item.count }}</td>
                  </tr>
                </tbody>
              </v-simple-table>
            </v-flex>
          </v-layout>
          <v-layout row align-center>
            <v-flex xs9>Add new fields, remove index docs</v-flex>
            <v-flex xs3 class="text-right">
              <v-btn :disabled="canRun(fcm_token)" color="accent" class="black--text" @click="fix">Fix</v-btn>
            </v-flex>
          </v-layout>

          <v-layout row class="py-1" align-center>
            <v-flex xs12>
              <h3 class="title">Cloud</h3>
            </v-flex>
            <v-flex xs9>Remove images from the Cloud not referenced in datastore</v-flex>
            <v-flex xs3 class="text-right">
              <v-btn :disabled="canRun(fcm_token)" color="error" @click="unbound">Remove</v-btn>
            </v-flex>
          </v-layout>
          <v-layout row class="py-1" align-center>
            <v-flex xs9>Remove images in datastore that are missing in the Cloud</v-flex>
            <v-flex xs3 class="text-right">
              <v-btn :disabled="canRun(fcm_token)" color="error" @click="missing">Missing</v-btn>
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
import firebase from '@firebase/app'
import '@firebase/messaging'

const messaging = firebase.messaging()

export default {
  name: 'Admin',
  mixins: [ common ],
  data: () => ({
    msg: {
      type: String,
      required: true,
      default: 'NEW IMAGES'
    },
    snackbar: false,
    timeout: 6000,
    message: ''
  }),
  created () {
    this.$store.dispatch('app/fetchStat')
  },
  mounted () {
    messaging.onMessage(payload => {
      this.message = payload.notification.body
      this.snackbar = true
    })
  },
  computed: {
    ...mapState('auth', ['fcm_token']),
    ...mapState('app', ['values', 'stat'])
  },
  methods: {
    canRun (token) {
      return Boolean(!token)
    },
    callAjax (url) {
      Vue.axios.post(url, { token: this.fcm_token })
        .then(
          this.$store.dispatch('app/fetchStat')
        )
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

<style scoped>
.v-btn {
  width: 100px;
}
</style>
