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
      <v-toolbar app dark color="secondary">
        <v-btn icon  @click="$router.push({name: 'home'})">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <v-toolbar-title class="headline">Admin</v-toolbar-title>
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
              <v-btn color="secondary" @click="send">Send</v-btn>
            </v-list-tile-action>
          </v-list-tile>
          <v-divider></v-divider>

          <v-subheader>Counters</v-subheader>
          <v-list-tile v-for="name in counters" :key="name" @click="nop">
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
import firebase from 'firebase/app'
import 'firebase/app'
import 'firebase/messaging'

const messaging = firebase.messaging()

export default {
  name: 'Admin',
  components: {
    'Footer': () => import('@/components/Footer')
  },
  data: () => ({
    text: '',
    snackbar: false,
    timeout: 6000,
    disabled: false
  }),
  created () {
    this.$store.dispatch('All/fetchInfo')
    this.$store.dispatch('All/fetchToken')
  },
  mounted () {
    messaging.onMessage(payload => {
      this.text = payload.notification.body
      this.snackbar = true
    })
  },
  computed: {
    ...mapState('All', ['counters', 'fcm_token'])
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
.list__tile__action .btn {
  width: 100px;
}
</style>
