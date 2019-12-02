<template>
  <v-list>
    <v-list-item v-if="authorized && $route.name !== 'add'" @click="$router.push({ name: 'add' })">
      <v-list-item-action>
        <v-icon>add_circle</v-icon>
      </v-list-item-action>
      <v-list-item-content>
        <v-list-item-title>Add</v-list-item-title>
      </v-list-item-content>
    </v-list-item>
    <v-list-item v-if="admin && $route.name !== 'admin'" @click="$router.push({ name: 'admin' })">
      <v-list-item-action>
        <v-icon>settings</v-icon>
      </v-list-item-action>
      <v-list-item-content>
        <v-list-item-title>Admin</v-list-item-title>
      </v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content class="caption">{{version}}</v-list-item-content>
    </v-list-item>
  </v-list>
</template>

<script>
import common from '@/helpers/mixins'

export default {
  name: 'Menu',
  mixins: [common],
  props: ['authorized', 'admin']
}
</script>
