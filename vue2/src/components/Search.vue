<template>
  <div>
    <Find :visible="showFindForm" @close="showFindForm = false"></Find>

    <v-app light>
      <v-toolbar app prominent extended>
        <v-icon @click="$router.push({name: 'home'})">arrow_back</v-icon>
        <v-toolbar-title class="headline">Results for</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-layout slot="extension">
          <v-toolbar-title>{{filter.value}}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-progress-circular v-show="busy" slot="extension" class="hidden-xs-only" color="primary" :indeterminate="true"></v-progress-circular>
          <v-btn icon @click="showFindForm = true">
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
import List from './List'
import Find from './Find'

export default {
  name: 'Search',
  components: {
    List,
    Find
  },
  data: () => ({
    showFindForm: false
  }),
  created () {
    this.$store.dispatch('getTags')
    this.$store.dispatch('getModels')
  },
  computed: {
    ...mapState(['filter', 'busy'])
  },
  destroyed () {
    this.$store.dispatch('changeFilter', {})
  }
}
</script>
