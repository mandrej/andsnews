<template>
  <v-list>
    <v-list-item two-line>
      <v-list-item-content>
        <v-list-item-title>{{total}}</v-list-item-title>
        <v-list-item-subtitle>photographs</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-list-item two-line>
      <v-list-item-content>
        <v-list-item-title>{{values.tags.length}}</v-list-item-title>
        <v-list-item-subtitle>tags</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-list-item two-line>
      <v-list-item-content>
        <v-list-item-title>{{values.model.length}}</v-list-item-title>
        <v-list-item-subtitle>cameras</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-list-item two-line>
      <v-list-item-content>
        <v-list-item-title>{{values.email.length}}</v-list-item-title>
        <v-list-item-subtitle>authors</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
  </v-list>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Stat',
  computed: {
    ...mapState('app', ['values', 'total'])
  }
}
</script>

<style scoped>
.v-list-item .v-list-item__title {
  font-size: 1.6rem;
}
</style>
