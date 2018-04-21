<template>
  <div>
    <v-snackbar
      v-model="snackbar"
      :timeout="timeout"
      left
      bottom>
      {{ text }}
      <v-btn flat color="white" @click.native="snackbar = false">Close</v-btn>
    </v-snackbar>

    <v-app light>
      <v-toolbar app flat>
        <v-icon @click="$router.push({name: 'home'})">arrow_back</v-icon>
        <h2 class="headline">Admin</h2>
        <v-spacer></v-spacer>
      </v-toolbar>

      <v-content>
        <v-container grid-list-md mt-3>
          <h1 class="headline">Photo {{count}}</h1>
          <v-layout row wrap>
            <v-flex v-for="name in counters" :key="name" xs6 sm4 md3>
              <v-btn large color="primary" @click="rebuild(name)">{{name}}</v-btn>
            </v-flex>
            <v-flex xs6 sm4 md3>
              <v-btn large color="secondary" @click="reindex">Photo Reindex</v-btn>
            </v-flex>
            <v-flex xs6 sm4 md3>
              <v-btn large color="secondary" @click="unbound">Photo Unbound</v-btn>
            </v-flex>
            <v-flex xs6 sm4 md3>
              <v-btn large disabled color="secondary" @click="fix">Deleted</v-btn>
            </v-flex>
          </v-layout>
        </v-container>
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
    this.$store.dispatch('getInfo')
    this.$store.dispatch('getToken')
  },
  mounted () {
    const messaging = firebase.messaging()
    messaging.onMessage(payload => {
      this.snackbar = true
      this.text = payload.notification.body
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
    handleMessage (e) {
      console.log(e.detail.message.notification.body)
    },
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
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.btn {
  width: 100%;
}
</style>
