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
      <v-toolbar app dark color="secondary" class="aperture">
        <v-btn icon @click="$router.push({ name: 'home' })">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <v-toolbar-title class="headline">Admin</v-toolbar-title>
      </v-toolbar>

      <v-content>
        <div class="pa-3 hidden-xs-only">
          <h2>Messaging</h2>
          <v-layout row justify-space-around>
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
            <v-flex xs1></v-flex>
            <v-flex xs2 class="pt-3 text-xs-right">
              <v-btn color="secondary" class="ma-0 pa-0" @click="send">Send</v-btn>
            </v-flex>
          </v-layout>
        </div>

        <v-list>
          <v-subheader>Counters</v-subheader>
          <v-divider></v-divider>
          <v-list-tile v-for="name in cloud" :key="name" @click="nop">
            <v-list-tile-content>
              <v-list-tile-title>Rebuild {{name}}</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-btn :disabled="disabled" color="secondary" @click="rebuild(name)">Rebuild</v-btn>
            </v-list-tile-action>
          </v-list-tile>

          <v-list-tile @click="nop">
            <v-list-tile-content>
              <v-list-tile-title>Reindex all images</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-btn :disabled="disabled" color="accent" class="black--text" @click="reindex">Reindex</v-btn>
            </v-list-tile-action>
          </v-list-tile>
          <v-divider></v-divider>

          <v-subheader>Cloud</v-subheader>
          <v-list-tile two-line @click="nop">
            <v-list-tile-content>
              <v-list-tile-title>Remove images from the Cloud</v-list-tile-title>
              <v-list-tile-sub-title>not referenced in datastore</v-list-tile-sub-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-btn :disabled="disabled" color="error" @click="unbound">Remove</v-btn>
            </v-list-tile-action>
          </v-list-tile>

          <v-list-tile two-line @click="nop">
            <v-list-tile-content>
              <v-list-tile-title>List images in datastore</v-list-tile-title>
              <v-list-tile-sub-title>that are missing in the Cloud</v-list-tile-sub-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-btn :disabled="disabled" color="secondary" @click="fix">Missing</v-btn>
            </v-list-tile-action>
          </v-list-tile>
        </v-list>
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
import 'firebase/app'
import 'firebase/messaging'

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
    disabled: false,
    msg: {
      type: String,
      required: true,
      default: 'NEW IMAGES'
    }
  }),
  created () {
    this.$store.dispatch('All/fetchCloud')
  },
  mounted () {
    messaging.onMessage(payload => {
      this.text = payload.notification.body
      this.snackbar = true
    })
  },
  computed: {
    ...mapState('All', ['cloud', 'fcm_token'])
  },
  watch: {
    fcm_token (val) {
      if (!val) {
        this.disabled = true
      }
    }
  },
  methods: {
    callAjax (url) {
      Vue.axios.post(url, {token: this.fcm_token})
        .then(x => x.data)
        // .catch(err => console.log(err))
    },
    rebuild (name) {
      this.callAjax('rebuild/' + name)
    },
    reindex () {
      this.callAjax('index/photo')
    },
    unbound () {
      this.callAjax('unbound/photo')
    },
    fix () {
      this.callAjax('fix/photo')
    },
    upper (event) {
      this.msg.default = event.toUpperCase()
    },
    send () {
      this.$store.dispatch('All/sendNotifications', this.msg.default)
    },
    nop () {
      return null
    }
  }
}
</script>

<style scoped>
.list__tile__action .btn {
  width: 100px;
}
</style>
