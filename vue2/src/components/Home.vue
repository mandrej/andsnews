<template>
  <div>
    <Find :visible="showFindForm" @close="showFindForm = false"></Find>
    <Add :visible="showAddForm" @close="showAddForm = false"></Add>

    <v-btn id="add" v-if="user.isAuthorized" fab medium color="accent" class="black--text" @click="showAddForm = true">
      <v-icon>add</v-icon>
    </v-btn>

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

    <v-app>
      <v-navigation-drawer v-model="drawer" fixed app>
        <v-toolbar extended dark color="red accent-3">
          <v-toolbar-title class="body-2 black--text">ANDS 2007-{{version}}</v-toolbar-title>
          <v-spacer></v-spacer>
          <SignIn></SignIn>
        </v-toolbar>

        <v-list>
          <v-list-tile @click="showFindForm = true">
            <v-list-tile-action>
              <v-icon>search</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Search</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
          <v-divider></v-divider>
          <v-list-tile @click="$router.push({name: 'admin'})">
            <v-list-tile-action>
              <v-icon>settings</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Admin</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </v-list>
      </v-navigation-drawer>

      <v-toolbar app extended dark color="primary">
        <v-toolbar-side-icon @click.native="drawer = !drawer"></v-toolbar-side-icon>
        <v-spacer></v-spacer>
        <v-layout slot="extension">
          <v-toolbar-title v-if="filter.value" style="margin-left: 0">
            <v-btn icon @click="clearFilter">
              <v-icon>close</v-icon>
            </v-btn>
            {{filter.value}}
          </v-toolbar-title>
          <v-toolbar-title v-else style="margin-left: 16px; font-size: 32px">{{title}}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-progress-circular v-show="busy" :indeterminate="true"></v-progress-circular>
          <v-btn v-if="!drawer" icon @click="showFindForm = true">
            <v-icon>search</v-icon>
          </v-btn>
        </v-layout>
      </v-toolbar>

      <v-content>
        <List></List>
      </v-content>
    </v-app>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import SignIn from './SignIn'
import List from './List'
import Find from './Find'
import Add from './Add'
import firebase from 'firebase'

export default {
  name: 'Home',
  components: {
    SignIn,
    List,
    Find,
    Add
  },
  props: ['version'],
  data: () => ({
    drawer: null,
    title: 'ANDрејевићи',
    showFindForm: false,
    showAddForm: false,
    text: '',
    snackbar: false,
    timeout: 6000
  }),
  created () {
    this.$store.dispatch('getToken')
    this.$store.dispatch('fetchTags')
    this.$store.dispatch('fetchModels')
  },
  mounted () {
    const messaging = firebase.messaging()
    messaging.onMessage(payload => {
      this.text = payload.notification.body
      this.snackbar = true
    })
  },
  computed: {
    ...mapState(['user', 'busy', 'filter'])
  },
  methods: {
    clearFilter () {
      this.$store.dispatch('changeFilter', {})
      this.$store.dispatch('fetchRecords')
    }
  }
}
</script>

<style lang="scss" scoped>
.body-2 {
  line-height: 48px;
}
#add {
  position: fixed;
  bottom: 16px;
  right: 32px;
  z-index: 10;
}
</style>
