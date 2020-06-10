<template>
  <v-list>
    <v-list-item two-line>
      <v-list-item-content>
        <v-list-item-title>{{formatBytes(bucket)}}</v-list-item-title>
        <v-list-item-subtitle>storage bucket size</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-divider></v-divider>
    <v-list-item two-line>
      <v-list-item-content>
        <v-list-item-title>{{total}}</v-list-item-title>
        <v-list-item-subtitle>photographs</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-divider></v-divider>
    <v-list-item two-line>
      <v-list-item-content>
        <v-list-item-title>{{values.tags.length}}</v-list-item-title>
        <v-list-item-subtitle>tags</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-divider></v-divider>
    <v-list-item two-line>
      <v-list-item-content>
        <v-list-item-title>{{values.model.length}}</v-list-item-title>
        <v-list-item-subtitle>cameras</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-divider></v-divider>
    <v-list-item two-line>
      <v-list-item-content>
        <v-list-item-title>{{values.email.length}}</v-list-item-title>
        <v-list-item-subtitle>authors</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-divider></v-divider>
  </v-list>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Stat',
  mixins: [common],
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
