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
import { mapState } from 'vuex'

export default {
  name: 'Item',
  data () {
    return {
      src: '/static/broken.svg',
      alt: '',
      title: 'Not found'
    }
  },
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
  // computed: {
  //   ...mapState({
  //     current: state => state.current,
  //     src: state => {
  //       if (state.current && state.current.serving_url) {
  //         if (process.env.NODE_ENV === 'development') {
  //           return state.current.serving_url.replace('http://localhost:8080/_ah', '/_ah') + '=s0'
  //         } else {
  //           return state.current.serving_url + '=s0'
  //         }
  //       } else {
  //         return '/static/broken.svg'
  //       }
  //     },
  //     alt: state => (state.current && state.current.slug) ? state.current.slug : '',
  //     title: state => (state.current && state.current.headline) ? state.current.headline : 'Not found'
  //   })
  // }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

</style>
