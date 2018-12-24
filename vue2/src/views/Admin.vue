<template>
  <div>
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

    <v-app>
      <v-toolbar app light class="aperture">
        <v-btn icon @click="$router.push({ name: 'home' })">
          <v-icon>home</v-icon>
        </v-btn>
        <v-toolbar-title class="headline">Admin</v-toolbar-title>
      </v-toolbar>

      <v-content>
        <v-container mt-4>
          <h3 class="title">Messaging</h3>
          <v-layout row>
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
            <v-flex xs3 class="pt-3 text-xs-right">
              <v-btn color="secondary" @click="send">Send</v-btn>
            </v-flex>
          </v-layout>

          <h3 class="title">Counters</h3>
          <v-divider></v-divider>
          <v-layout row v-for="field in keys(values)" :key="field">
            <v-flex xs9>
              <v-layout align-center fill-height>
                Rebuild for field {{field}}
              </v-layout>
            </v-flex>
            <v-flex xs3 class="text-xs-right">
              <v-btn :disabled="canRun(fcm_token)" color="secondary" @click="rebuild(field)">Rebuild</v-btn>
            </v-flex>
          </v-layout>
          <v-layout row>
            <v-flex xs9>
              <v-layout align-center fill-height>
                Reindex all images
              </v-layout>
            </v-flex>
            <v-flex xs3 class="text-xs-right">
              <v-btn :disabled="canRun(fcm_token)" color="accent" class="black--text" @click="reindex">Reindex</v-btn>
            </v-flex>
          </v-layout>
          <v-layout row>
            <v-flex xs9>
              <v-layout align-center fill-height>
                Remove google.appengine.api.users
              </v-layout>
            </v-flex>
            <v-flex xs3 class="text-xs-right">
              <v-btn :disabled="canRun(fcm_token)" color="accent" class="black--text" @click="fix">Fix</v-btn>
            </v-flex>
          </v-layout>

          <h3 class="title">Cloud</h3>
          <v-divider></v-divider>
          <v-layout row>
            <v-flex xs9>
              <v-layout align-center fill-height>
                Remove images from the Cloud not referenced in datastore
              </v-layout>
            </v-flex>
            <v-flex xs3 class="text-xs-right">
              <v-btn :disabled="canRun(fcm_token)" color="error" @click="unbound">Remove</v-btn>
            </v-flex>
          </v-layout>
          <v-layout row>
            <v-flex xs9>
              <v-layout align-center fill-height>
                Remove images in datastore that are missing in the Cloud
              </v-layout>
            </v-flex>
            <v-flex xs3 class="text-xs-right">
              <v-btn :disabled="canRun(fcm_token)" color="error" @click="missing">Missing</v-btn>
            </v-flex>
          </v-layout>
        </v-container>
      </v-content>

      <Footer/>
    </v-app>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import common from '@/helpers/mixins'
import firebase from 'firebase/app'

const messaging = firebase.messaging()

export default {
  name: 'Admin',
  components: {
    'Footer': () => import(/* webpackChunkName: "footer" */ '@/components/Footer')
  },
  mixins: [ common ],
  data: () => ({
    text: '',
    snackbar: false,
    timeout: 6000,
    msg: {
      type: String,
      required: true,
      default: 'NEW IMAGES'
    }
  }),
  created () {
    this.$store.dispatch('auth/fetchToken')
  },
  mounted () {
    messaging.onMessage(payload => {
      this.text = payload.notification.body
      this.snackbar = true
    })
  },
  computed: {
    ...mapState('auth', ['fcm_token']),
    ...mapState('app', ['values'])
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
    },
    keys (values) {
      return Object.keys(values)
    }
  }
}
</script>

<style scoped>
.list__tile__action .btn {
  width: 100px;
}
</style>
