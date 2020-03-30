<template>
  <Layout>
    <v-container my-10>
      <h1>{{title}}</h1>
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
