<template>
  <v-container>
    <h1>{{title}}</h1>
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
        <v-btn color="primary" width="100" @click="send">Send</v-btn>
      </v-flex>
    </v-layout>

    <h3 class="title">Counters</h3>
    <v-layout wrap align-center v-for="field in Object.keys(values)" :key="field" class="py-1">
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
      <v-flex xs9>Save all records to use &lt;int:id&gt; instead of &lt;str:id_or_name&gt;</v-flex>
      <v-flex xs3 class="text-right">
        <v-btn :disabled="true" color="primary" width="100" @click="fix">Fix</v-btn>
      </v-flex>
    </v-layout>-->

    <h3 class="title">Google Cloud Storage</h3>
    <v-layout wrap class="py-1" align-center>
      <v-flex xs9>Bucket count and size</v-flex>
      <v-flex xs3 class="text-right">
        <v-btn width="100" color="primary" @click="bucket">Rebuild</v-btn>
      </v-flex>
    </v-layout>
    <v-layout wrap class="py-1" align-center>
      <v-flex xs9>Remove images from the Cloud not referenced in datastore (SLOW)</v-flex>
      <v-flex xs3 class="text-right">
        <v-btn :disabled="canRun(fcm_token)" color="error" width="100" @click="unbound">Remove</v-btn>
      </v-flex>
    </v-layout>
    <v-layout wrap class="py-1" align-center>
      <v-flex xs9>Remove datastore records with images missing in the Cloud (404)</v-flex>
      <v-flex xs3 class="text-right">
        <v-btn :disabled="true" color="error" width="100" @click="missing">Missing</v-btn>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Admin',
  props: ['title'],
  mixins: [common],
  data: () => ({
    msg: {
      type: String,
      required: true,
      default: 'NEW IMAGES'
    }
  }),
  computed: {
    ...mapState('auth', ['fcm_token']),
    ...mapState('app', ['values'])
  },
  mounted () {
    this.$store.dispatch('auth/fetchToken')
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
    bucket () {
      this.$store.dispatch('app/bucketInfo', { verb: 'set' })
    }
  }
}
</script>
