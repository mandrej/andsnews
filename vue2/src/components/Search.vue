<template>
  <div>
    <Find :visible="showFindForm" @close="showFindForm = false"></Find>

    <v-app light>
      <v-toolbar app flat>
        <v-icon @click="$router.push({name: 'home'})">arrow_back</v-icon>
        <h2 class="headline">Search results</h2>
        <v-spacer></v-spacer>
        <v-btn icon @click="showFindForm = true">
          <v-icon>search</v-icon>
        </v-btn>
      </v-toolbar>

      <v-content>
        <List></List>
      </v-content>
    </v-app>
  </div>
</template>

<script>
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
  destroyed () {
    this.$store.dispatch('changeFilter', {})
  }
}
</script>
