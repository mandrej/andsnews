<template>
  <v-list>
    <v-list-item @click="signHandler">
      <v-list-item-action>
        <v-icon>account_circle</v-icon>
      </v-list-item-action>
      <v-list-item-content>
        <template v-if="user.name">
          <v-list-item-title>Sign out</v-list-item-title>
          <v-list-item-subtitle>{{ user.name }}</v-list-item-subtitle>
        </template>
        <template v-else>
          <v-list-item-title>Sign in</v-list-item-title>
          <v-list-item-subtitle>using your Google account</v-list-item-subtitle>
        </template>
      </v-list-item-content>
    </v-list-item>
    <v-list-item v-show="user.isAuthorized" to="/add">
      <v-list-item-action>
        <v-icon>add_circle</v-icon>
      </v-list-item-action>
      <v-list-item-content>
        <v-list-item-title>Add</v-list-item-title>
        <v-list-item-subtitle>jpeg images less then 4 Mb</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-list-item v-show="user.isAdmin" to="/admin">
      <v-list-item-action>
        <v-icon>settings</v-icon>
      </v-list-item-action>
      <v-list-item-content>
        <v-list-item-title>Admin</v-list-item-title>
        <v-list-item-subtitle>rebuild various counters</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-list-item @click="switchTheme">
      <v-list-item-action>
        <v-icon>palette</v-icon>
      </v-list-item-action>
      <v-list-item-content>
        <v-list-item-title v-if="$vuetify.theme.dark">Light</v-list-item-title>
        <v-list-item-title v-else>Dark</v-list-item-title>
        <v-list-item-subtitle>change application theme</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content class="text-caption">{{
        version
      }}</v-list-item-content>
    </v-list-item>
  </v-list>
</template>

<script>
import { mapState } from 'vuex'
import common from '../helpers/mixins'

export default {
  name: 'Menu',
  mixins: [common],
  computed: {
    ...mapState('auth', ['user'])
  },
  methods: {
    signHandler () {
      this.$store.dispatch('auth/signIn')
    },
    switchTheme () {
      this.$vuetify.theme.dark = !this.$vuetify.theme.dark
      this.$store.dispatch('app/toggleTheme', this.$vuetify.theme.dark)
    }
  }
}
</script>
