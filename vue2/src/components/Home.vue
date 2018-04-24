<template>
  <div>
    <Find :visible="showFindForm" @close="showFindForm = false"></Find>
    <Add :visible="showAddForm" @close="showAddForm = false"></Add>
    <v-btn id="add" v-if="user.isAuthorized" fab medium color="warning" class="secondary--text" @click="showAddForm = true">
      <v-icon>add</v-icon>
    </v-btn>

    <v-app light>
      <v-toolbar app prominent extended>
        <v-toolbar-title class="headline">{{title}}</v-toolbar-title>
        <v-spacer></v-spacer>
        <SignIn></SignIn>
        <v-layout slot="extension">
          <v-spacer ></v-spacer>
          <v-progress-circular v-show="busy" color="primary" :indeterminate="true"></v-progress-circular>
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
import SignIn from './SignIn'
import List from './List'
import Find from './Find'
import Add from './Add'

export default {
  name: 'Home',
  components: {
    SignIn,
    List,
    Find,
    Add
  },
  data: () => ({
    drawer: null,
    title: 'ANDрејевићи',
    showFindForm: false,
    showAddForm: false
  }),
  created () {
    this.$store.dispatch('getTags')
    this.$store.dispatch('getModels')
  },
  computed: {
    ...mapState(['user', 'busy'])
  }
}
</script>

<style lang="scss" scoped>
#add {
  position: fixed;
  bottom: 16px;
  right: 32px;
  z-index: 10;
}
</style>
