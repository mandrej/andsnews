<template>
  <v-app light>
    <v-toolbar app>
      <v-icon @click="$router.go(-1)">arrow_back</v-icon>
      <v-toolbar-title>{{title}}</v-toolbar-title>
    </v-toolbar>

    <v-content>
      <img :src="src" :alt="alt">
    </v-content>
  </v-app>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Item',
  data: () => ({
    src: '/static/broken.svg',
    alt: '',
    title: 'Not found'
  }),
  created () {
    this.$store.dispatch('getRecord', this.$route.params.id)
  },
  computed: {
    ...mapState(['current'])
  },
  watch: {
    current (newVal, oldVal) {
      if (!newVal) return
      this.createRecord(newVal)
    }
  },
  methods: {
    createRecord (obj) {
      this.title = obj.headline
      this.src = (process.env.NODE_ENV === 'development') ? obj.serving_url.replace('http://localhost:8080/_ah', '/_ah') + '=s0' : obj.serving_url + '=s0'
      this.alt = obj.slug
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
img {
  width: 100%;
}
</style>
