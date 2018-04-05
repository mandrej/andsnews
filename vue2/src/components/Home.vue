<template>
  <div class="page-container">
    <md-app>
      <md-app-toolbar class="md-primary">
        <span class="md-title">{{msg}}</span>
      </md-app-toolbar>

      <md-app-content>
        <div class="md-layout md-gutter">
          <div class="md-layout-item md-xsmall-size-100 md-small-size-50 md-medium-size-33 md-large-size-25"
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
        </div>
      </md-app-content>
    </md-app>
  </div>
</template>

<script>
import Vuex from 'vuex'
import store from '../store'

export default {
  name: 'Home',
  data () {
    return {
      msg: 'ANDS'
    }
  },
  computed: Vuex.mapState(['objects', 'page', 'next', 'loading']),
  store,
  created () {
    // console.log(this.$store)
    this.$store.dispatch('loadData') // dispatch loading
  },
  methods: {
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
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.md-card {
  width: 100%;
  margin: 0 0 16px;
  display: inline-block;
  vertical-align: top;
}
</style>
