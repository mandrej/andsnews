<template>
  <div class="page-container">
    <md-app>
      <md-app-toolbar class="md-primary">
        <span class="md-title">{{title}}</span>
      </md-app-toolbar>

      <md-app-content>
        <img :src="`${src}`" :alt="`${alt}`">
      </md-app-content>
    </md-app>
  </div>
</template>

<script>
import Vuex from 'vuex'

export default {
  name: 'Item',
  computed: Vuex.mapState({
    current: state => state.current,
    src: state => {
      if (state.current && state.current.serving_url) {
        if (process.env.NODE_ENV === 'development') {
          return state.current.serving_url.replace('http://localhost:8080/_ah', '/_ah') + '=s0'
        } else {
          return state.current.serving_url + '=s0'
        }
      } else {
        return '/static/broken.svg'
      }
    },
    alt: state => {
      if (state.current && state.current.slug) {
        return state.current.slug
      } else {
        return ''
      }
    },
    title: state => {
      if (state.current && state.current.headline) {
        return state.current.headline
      } else {
        return 'Not found'
      }
    }
  }),
  created () {
    this.$store.dispatch('getData', this.$route.params.id)
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

</style>
