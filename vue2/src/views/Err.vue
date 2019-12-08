<template>
  <Layout>
    <template v-slot:appbar>
      <v-app-bar app dark color="primary">
        <v-avatar size="40px" @click="$router.push({ name: 'home' })" style="cursor: pointer">
          <v-img src="/static/img/aperture.svg" class="mr-3"></v-img>
        </v-avatar>
        <v-toolbar-title class="headline">{{title}}</v-toolbar-title>
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
