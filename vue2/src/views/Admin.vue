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
      <v-navigation-drawer v-model="drawer" app fixed>
        <v-toolbar dark color="red accent-3">
          <v-spacer></v-spacer>
          <SignIn></SignIn>
          <v-layout slot="extension">
            <v-toolbar-title style="font-size: 32px">{{total}}</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-layout>
        </v-toolbar>

        <!-- <v-list>
          <v-list-tile two-line>
            <v-list-tile-content>
              <v-list-tile-title></v-list-tile-title>
              <v-list-tile-sub-title></v-list-tile-sub-title>
            </v-list-tile-content>
          </v-list-tile>
        </v-list> -->
      </v-navigation-drawer>

      <v-toolbar app dark color="primary">
        <v-toolbar-side-icon @click="drawer = !drawer"></v-toolbar-side-icon>
        <v-spacer></v-spacer>
        <v-layout slot="extension">
          <v-btn icon  @click="$router.push({name: 'home'})">
            <v-icon>arrow_back</v-icon>
          </v-btn>
          <v-toolbar-title style="font-size: 32px">Admin</v-toolbar-title>
        </v-layout>
      </v-toolbar>

      <v-content>
        <v-list>
          <v-subheader>Messaging</v-subheader>
          <v-list-tile two-line @click="nop">
            <v-list-tile-content>
              <v-list-tile-title>Send message</v-list-tile-title>
              <v-list-tile-sub-title>to subscribers group</v-list-tile-sub-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-btn color="primary" @click="send">Send</v-btn>
            </v-list-tile-action>
          </v-list-tile>
          <v-divider></v-divider>

          <v-subheader>Counters</v-subheader>
          <v-list-tile v-for="name in counters" :key="name" @click="nop">
            <v-list-tile-content>
              <v-list-tile-title>Rebuild {{name}}</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-btn :disabled="disabled" color="primary" @click="rebuild(name)">Rebuild</v-btn>
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

      <Footer :version="version"></Footer>
    </v-app>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import SignIn from '@/components/SignIn'
import Footer from '@/components/Footer'
import firebase from 'firebase/app'
import 'firebase/app'
import 'firebase/messaging'

const messaging = firebase.messaging()

export default {
  name: 'Admin',
  components: {
    SignIn,
    Footer
  },
  props: ['version'],
  data: () => ({
    drawer: null,
    text: '',
    snackbar: false,
    timeout: 3000,
    disabled: (process.env.NODE_ENV === 'development')
  }),
  created () {
    this.$store.dispatch('All/fetchInfo')
  },
  mounted () {
    messaging.onMessage(payload => {
      this.text = payload.notification.body
      this.snackbar = true
    })
  },
  computed: {
    ...mapState('All', ['total', 'counters', 'fcm_token'])
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
    send () {
      this.$store.dispatch('All/sendNotifications')
    },
    nop () {
      return null
    }
  }
}
</script>

<style scoped>
.body-2 {
  line-height: 48px;
}
.list__tile__action .btn {
  width: 100px;
}
</style>
