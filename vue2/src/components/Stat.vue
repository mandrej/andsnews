<template>
  <v-list>
    <template v-for="(item, index) in list">
      <v-list-item :key="item.icon" two-line @click.prevent>
        <v-list-item-content>
          <v-list-item-title>{{item.value}}</v-list-item-title>
          <v-list-item-subtitle>{{item.text}}</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
      <v-divider v-if="index + 1 < list.length" :key="index"></v-divider>
    </template>
  </v-list>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Stat',
  mixins: [common],
  computed: {
    ...mapState('app', ['values', 'bucket']),
    list () {
      return [
        {
          value: this.bucket.count,
          text: 'photographs'
        },
        {
          value: this.formatBytes(this.bucket.size),
          text: 'storage size'
        },
        {
          value: this.values.tags.length,
          text: 'tags'
        },
        {
          value: this.values.model.length,
          text: 'cameras'
        },
        {
          value: this.values.email.length,
          text: 'authors'
        }
      ]
    }
  }
}
</script>

<style scoped>
.v-list-item .v-list-item__title {
  font-size: 1.6rem;
}
</style>
