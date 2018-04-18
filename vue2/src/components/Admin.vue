<template>
  <v-app light>
    <v-toolbar app>
      <v-icon @click="$router.push({name: 'home'})">arrow_back</v-icon>
      <v-toolbar-title>Admin</v-toolbar-title>
      <v-spacer></v-spacer>
    </v-toolbar>

    <v-content>
      <v-container grid-list-md mt-3>
        <h1 class="headline">Photo {{count}}</h1>
        <v-layout row wrap>
          <v-flex v-for="name in counters" :key="name" xs12 sm6 md4>
            <v-btn large color="primary" @click="rebuild(name)">{{name}}</v-btn>
          </v-flex>
          <v-flex xs12 sm6 md4>
            <v-btn large color="secondary" @click="reindex">Photo Reindex</v-btn>
          </v-flex>
          <v-flex xs12 sm6 md4>
            <v-btn large color="secondary" @click="unbound">Photo Unbound</v-btn>
          </v-flex>
          <v-flex xs12 sm6 md4>
            <v-btn large disabled color="secondary" @click="fix">Deleted</v-btn>
          </v-flex>
        </v-layout>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import { mapState } from 'vuex'
import { HTTP } from '../../config/http'

export default {
  name: 'Admin',
  data: () => ({
    count: 0,
    counters: [],
    token: null
  }),
  created () {
    this.$store.dispatch('getInfo')
    // this.getToken()
  },
  computed: {
    ...mapState(['info'])
  },
  watch: {
    info (newVal, oldVal) {
      if (!newVal) return
      this.count = newVal.photo.count
      this.counters = newVal.photo.counters
    }
  },
  methods: {
    getToken () {
      this.$FireMessaging.getToken()
        .then(token => console.log(token))
        .catch(() => console.log('token failed'))
    },
    callAjax (url) {
      this.$FireMessaging.requestPermission()
        .then(() => {
          HTTP.post(url, {token: 'SDFSDFSDFFSDFSDFSDF'})
            .then(x => x.data)
            .catch(err => console.log(err))
        })
        .catch(() => console.log('permission failed'))
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
