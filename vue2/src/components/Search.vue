<template>
  <v-app light>
    <v-toolbar app>
      <v-icon @click="$router.push({name: 'home'})">arrow_back</v-icon>
      <v-toolbar-title>Search results</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon :to="{ name: 'find' }">
        <v-icon>search</v-icon>
      </v-btn>
    </v-toolbar>

    <v-content>
      <List></List>
    </v-content>
  </v-app>
</template>

<script>
import List from './List'

export default {
  name: 'Search',
  components: {
    List
  },
  destroyed () {
    this.$store.dispatch('changeFilter', {})
  }
}
</script>
