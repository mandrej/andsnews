<template>
  <div>
    <Find :visible="showFindForm" @close="showFindForm = false"></Find>
    <Add :visible="showAddForm" @close="showAddForm = false"></Add>

    <v-btn id="add" v-if="user.isAuthorized" fab medium color="warning" class="secondary--text" @click="showAddForm = true">
      <v-icon>add</v-icon>
    </v-btn>

    <v-app>
      <v-toolbar app prominent extended flat>
        <v-toolbar-title style="font-size: 32px">{{title}}</v-toolbar-title>
        <v-spacer></v-spacer>
        <SignIn></SignIn>
        <v-layout slot="extension">
          <v-toolbar-title v-if="filter.value">
            <v-btn icon color="secondary--text" @click="clearFilter">
              <v-icon>close</v-icon>
            </v-btn>
            {{filter.value}}
          </v-toolbar-title>
          <v-toolbar-title v-else class="grey--text text--lighten-1">ANDS 2007-{{version}}</v-toolbar-title>
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
import { EventBus } from '../../helpers/event-bus'

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
    showAddForm: false
  }),
  created () {
    this.$store.dispatch('fetchTags')
    this.$store.dispatch('fetchModels')
  },
  mounted () {
    EventBus.$on('reload', () => {
      this.$store.dispatch('fetchRecords')
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
#add {
  position: fixed;
  bottom: 16px;
  right: 32px;
  z-index: 10;
}
</style>
