<template>
  <v-list>
    <v-list-item @click="signHandler">
      <v-list-item-action>
        <v-icon color="info">account_circle</v-icon>
      </v-list-item-action>
      <v-list-item-content>
        <template v-if="user.name">
          <v-list-item-title>Sign out</v-list-item-title>
          <v-list-item-subtitle>{{user.name}}</v-list-item-subtitle>
        </template>
        <template v-else>
          <v-list-item-title>Sign in</v-list-item-title>
          <v-list-item-subtitle>using your Google account</v-list-item-subtitle>
        </template>
      </v-list-item-content>
    </v-list-item>
    <v-list-item v-if="user.isAuthorized && $route.name !== 'add'" to="/add">
      <v-list-item-action>
        <v-icon color="info">add_circle</v-icon>
      </v-list-item-action>
      <v-list-item-content>
        <v-list-item-title>Add</v-list-item-title>
        <v-list-item-subtitle>jpeg images less then 4 Mb</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-list-item v-if="user.isAdmin && $route.name !== 'admin'" to="/admin">
      <v-list-item-action>
        <v-icon color="info">settings</v-icon>
      </v-list-item-action>
      <v-list-item-content>
        <v-list-item-title>Admin</v-list-item-title>
        <v-list-item-subtitle>set various counters</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-list-item @click="switchTheme">
      <v-list-item-action>
        <v-icon color="info">palette</v-icon>
      </v-list-item-action>
      <v-list-item-content>
        <v-list-item-title v-if="$vuetify.theme.dark">Light</v-list-item-title>
        <v-list-item-title v-else>Dark</v-list-item-title>
        <v-list-item-subtitle>change application theme</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content class="caption">{{version}}</v-list-item-content>
    </v-list-item>
  </v-list>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

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
