<template>
  <v-list>
    <v-list-item v-if="authorized" @click="$router.push({ name: 'add' })">
      <v-list-item-action>
        <v-icon>add_circle</v-icon>
      </v-list-item-action>
      <v-list-item-content>
        <v-list-item-title>Add</v-list-item-title>
      </v-list-item-content>
    </v-list-item>
    <v-list-item v-if="admin" @click="$router.push({ name: 'admin' })">
      <v-list-item-action>
        <v-icon>settings</v-icon>
      </v-list-item-action>
      <v-list-item-content>
        <v-list-item-title>Admin</v-list-item-title>
      </v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content class="caption">© 2007-{{version}}</v-list-item-content>
    </v-list-item>
  </v-list>
</template>

<script>
export default {
  name: 'Menu',
  props: ['authorized', 'admin'],
  computed: {
    version () {
      return process.env.VUE_APP_VERSION.match(/.{1,4}/g).join('.')
    }
  }
}
</script>
