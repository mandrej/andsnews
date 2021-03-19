<template>
  <v-container>
    <v-list color="transparent">
      <h3>Send message to subscribers</h3>
      <v-list-item>
        <v-list-item-content>
          <v-text-field
            label="Message"
            hint="Send message to subscribers group"
            v-model="msg.default"
            type="text"
            @input="upper($event)"
            :rules="requiredRule"
            required
          ></v-text-field>
        </v-list-item-content>
        <v-list-item-action>
          <v-btn color="primary" @click="send">Send</v-btn>
        </v-list-item-action>
      </v-list-item>

      <h3>Rebuild counters</h3>
      <v-list-item v-for="field in Object.keys(values)" :key="field">
        <v-list-item-content>
          <v-list-item-title>for {{field}}</v-list-item-title>
        </v-list-item-content>
        <v-list-item-action>
          <v-btn-toggle v-model="key">
            <v-btn
              :disabled="canRun(fcm_token)"
              color="primary"
              width="100"
              @click="rebuild(field)"
            >Rebuild</v-btn>
          </v-btn-toggle>
        </v-list-item-action>
      </v-list-item>

      <h3>Bug fix on {{$date('2021-03-08').format('dddd, MMMM DD, YYYY')}}</h3>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>Datastore lens fix</v-list-item-title>
        </v-list-item-content>
        <v-list-item-action>
          <v-btn-toggle v-model="toggleFix">
            <v-btn :disabled="canRun(fcm_token)" color="primary" @click="fix">Fix</v-btn>
          </v-btn-toggle>
        </v-list-item-action>
      </v-list-item>

      <h3>Storage</h3>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>Bucket count and size</v-list-item-title>
        </v-list-item-content>
        <v-list-item-action>
          <v-btn-toggle v-model="toggleBucket">
            <v-btn color="primary" @click="bucket">Rebuild</v-btn>
          </v-btn-toggle>
        </v-list-item-action>
      </v-list-item>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>Synchronize datastore records and Cloud bucket</v-list-item-title>
        </v-list-item-content>
        <v-list-item-action>
          <v-btn-toggle v-model="toggleMissing">
            <v-btn :disabled="canRun(fcm_token)" color="error" @click="repair">Repair</v-btn>
          </v-btn-toggle>
        </v-list-item-action>
      </v-list-item>
    </v-list>
  </v-container>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Admin',
  mixins: [common],
  data: () => ({
    toggleFix: undefined,
    toggleBucket: undefined,
    toggleRepair: undefined,
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
    repair () {
      this.callAjax('repair')
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

<style scoped>
.v-btn-toggle:not(.v-btn-toggle--dense) .v-btn.v-btn.v-size--default {
  height: 36px;
}
.v-btn {
  width: 100px;
}
.v-list-item__action {
  margin: 0;
}
</style>
