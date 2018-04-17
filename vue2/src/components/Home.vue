<template>
  <div>
    <Find :visible="showFindForm" @close="showFindForm=false"></Find>

    <v-app light>
      <v-btn id="add" v-if="user.isAuthorized" fab medium color="warning" class="secondary--text" @click="$router.push({name: 'add'})">
        <v-icon>add</v-icon>
      </v-btn>

      <v-toolbar app>
        <v-toolbar-title>{{title}}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon @click="showFindForm=true">
          <v-icon>search</v-icon>
        </v-btn>
        <SignIn></SignIn>
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

export default {
  name: 'Home',
  components: {
    SignIn,
    List,
    Find
  },
  data: () => ({
    drawer: null,
    title: 'ANDрејевићи',
    showFindForm: false
  }),
  computed: {
    ...mapState(['user'])
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
