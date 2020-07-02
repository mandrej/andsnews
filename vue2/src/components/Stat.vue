<template>
  <v-list>
    <v-list-item two-line>
      <v-list-item-content>
        <v-list-item-title>{{bucket.count}}</v-list-item-title>
        <v-list-item-subtitle>photographs</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-divider></v-divider>
    <v-list-item two-line>
      <v-list-item-content>
        <v-list-item-title>{{formatBytes(bucket.size)}}</v-list-item-title>
        <v-list-item-subtitle>storage size</v-list-item-subtitle>
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
  created () {
    this.$store.dispatch('app/getBucketInfo')
  },
  computed: {
    ...mapState('app', ['values', 'bucket'])
  }
}
</script>

<style scoped>
.v-list-item .v-list-item__title {
  font-size: 1.6rem;
}
</style>
