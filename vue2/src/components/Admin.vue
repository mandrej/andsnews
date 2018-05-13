<template>
  <div>
    <v-snackbar
      v-model="snackbar"
      :timeout="timeout"
      left
      bottom>
      {{ text }}
      <v-btn flat icon color="white" @click.native="snackbar = false">
        <v-icon>close</v-icon>
      </v-btn>
    </v-snackbar>

    <v-app light>
      <v-toolbar app prominent extended flat>
        <v-icon @click="$router.push({name: 'home'})" style="cursor: pointer">arrow_back</v-icon>
        <v-toolbar-title class="headline">Background admin operations</v-toolbar-title>
        <v-toolbar-title slot="extension">{{count}} photos and counting</v-toolbar-title>
      </v-toolbar>

      <v-content>
        <v-list>
          <v-subheader>Counters</v-subheader>

          <v-list-tile v-for="name in counters" :key="name" @click="nop">
            <v-list-tile-content>
              <v-list-tile-title>Rebuild {{name}}</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-btn color="primary" @click="rebuild(name)">Rebuild</v-btn>
            </v-list-tile-action>
          </v-list-tile>

          <v-list-tile @click="nop">
            <v-list-tile-content>
              <v-list-tile-title>Reindex all images</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-btn color="accent" class="black--text" @click="reindex">Reindex</v-btn>
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
              <v-btn color="error" @click="unbound">Remove</v-btn>
            </v-list-tile-action>
          </v-list-tile>

          <v-list-tile two-line @click="nop">
            <v-list-tile-content>
              <v-list-tile-title>List images in datastore</v-list-tile-title>
              <v-list-tile-sub-title>that are missing in the Cloud</v-list-tile-sub-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-btn color="secondary" @click="fix">Missing</v-btn>
            </v-list-tile-action>
          </v-list-tile>
        </v-list>
      </v-content>
    </v-app>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { HTTP } from '../../helpers/http'
import firebase from 'firebase'

export default {
  name: 'Admin',
  data: () => ({
    count: 0,
    counters: [],
    text: '',
    snackbar: false,
    timeout: 3000
  }),
  created () {
    this.$store.dispatch('fetchInfo')
  },
  mounted () {
    const messaging = firebase.messaging()
    messaging.onMessage(payload => {
      this.text = payload.notification.body
      this.snackbar = true
    })
  },
  computed: {
    ...mapState(['info', 'fcm_token'])
  },
  watch: {
    info (newVal, oldVal) {
      if (!newVal) return
      this.count = newVal.photo.count
      this.counters = newVal.photo.counters
    }
  },
  methods: {
    callAjax (url) {
      HTTP.post(url, {token: this.fcm_token})
        .then(x => x.data)
        .catch(err => console.log(err))
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
    nop () {
      return null
    }
  }
}
</script>

<style lang="scss" scoped>
.btn {
  width: 100px;
}
</style>
