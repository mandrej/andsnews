<template>
  <Layout>
    <template v-slot:appbar>
      <v-app-bar app>
        <v-toolbar-title
          class="headline"
          @click="$router.push({ name: 'home' })"
          style="cursor: pointer; padding-left: 0"
        >{{title}}</v-toolbar-title>
      </v-app-bar>
    </template>

    <v-container my-10>
      <v-alert type="error" transition="scale-transition" prominent>{{text}}</v-alert>
    </v-container>
  </Layout>
</template>

<script>
import Layout from '@/components/Layout'

export default {
  name: 'Err',
  components: {
    Layout
  },
  props: ['title', 'text']
}
</script>
