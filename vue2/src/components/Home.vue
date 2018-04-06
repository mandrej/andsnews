<template>
  <div class="page-container">
    <md-app>
      <md-app-toolbar class="md-primary">
        <span class="md-title">{{title}}</span>
      </md-app-toolbar>

      <md-app-content>
        <div class="md-layout md-gutter">
          <div class="md-layout-item md-xsmall-size-100 md-small-size-50 md-medium-size-33 md-large-size-25 md-size-20"
            v-for="item in objects" :key="item.safekey">
            <md-card>
              <md-card-media-cover md-solid>
                <md-card-media md-ratio="1/1">
                  <img :src="findImage(item)" :alt="`${item.slug}`">
                </md-card-media>
                <md-card-area>
                  <md-card-header>
                    <span class="md-title">{{item.headline}}</span>
                    <span class="md-subhead">{{item.date}}</span>
                  </md-card-header>
                </md-card-area>
              </md-card-media-cover>
            </md-card>
          </div>
          <infinite-loading @infinite="infiniteHandler"
            force-use-infinite-wrapper="true" :distance="distance" ref="infiniteLoading">
            <span slot="no-results">No results</span>
            <span slot="no-more">No more</span>
          </infinite-loading>
        </div>
      </md-app-content>
    </md-app>
  </div>
</template>

<script>
import Vuex from 'vuex'
import store from '../store'
import InfiniteLoading from 'vue-infinite-loading'

export default {
  name: 'Home',
  data () {
    return {
      title: 'ANDS',
      distance: 100
    }
  },
  store,
  computed: Vuex.mapState(['objects', 'page', 'next', 'loading']),
  created () {
    // this.$store.dispatch('resetData')
    this.$store.dispatch('loadData') // dispatch loading
  },
  methods: {
    infiniteHandler ($state) {
      if (this.next && !this.loading) {
        this.$store.dispatch('loadData', this.next)
        $state.loaded()
      } else {
        $state.complete()
      }
    },
    findImage (rec) {
      if (rec && rec.serving_url) {
        if (process.env.NODE_ENV === 'development') {
          return rec.serving_url.replace('http://localhost:8080/_ah', '/_ah') + '=s400-c'
        } else {
          return rec.serving_url + '=s400-c'
        }
      } else {
        return '/static/broken.svg'
      }
    }
  },
  components: {
    InfiniteLoading
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
// md-app-content {
//   max-height: 100%;
// }
.md-card {
  width: 100%;
  margin: 0 0 16px;
  display: inline-block;
  vertical-align: top;
}
</style>
