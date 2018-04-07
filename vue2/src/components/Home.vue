<template>
  <div class="page-container">
    <md-app>
      <md-app-toolbar class="md-primary">
        <span class="md-title">{{title}}</span>
      </md-app-toolbar>

      <md-app-content>
        <div v-infinite-scroll="loadMore" infinite-scroll-disabled="loading" infinite-scroll-distance="10">
          <div class="grid">
            <div v-masonry transition-duration="0.3s" item-selector=".grid-item"
              horizontal-order="true" column-width=".grid-sizer" gutter=".gutter-sizer">
              <div class="grid-sizer"></div>
              <div class="gutter-sizer"></div>
              <div v-masonry-tile class="grid-item" v-for="item in objects" :key="item.safekey">
                <router-link :to="{ name: 'item', params: { id: item.safekey }}">
                  <img :src="src(item)" :alt="`${item.slug}`" class="md-elevation-1">
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </md-app-content>
      <!-- <router-link :to="{ name: 'edit', params: { id: item.safekey }}">
        <md-button>Edit</md-button>
      </router-link> -->
    </md-app>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import { VueMasonryPlugin } from 'vue-masonry'
import infiniteScroll from 'vue-infinite-scroll'

Vue.use(VueMasonryPlugin, infiniteScroll)

export default {
  name: 'Home',
  data () {
    return {
      title: 'ANDS'
    }
  },
  created () {
    this.$store.dispatch('loadList')
  },
  computed: {
    ...mapState(['objects', 'page', 'next', 'loading'])
  },
  methods: {
    loadMore () {
      if (this.next) {
        this.$store.dispatch('loadList', this.next)
      }
    },
    src (rec) {
      if (rec && rec.serving_url) {
        if (process.env.NODE_ENV === 'development') {
          return rec.serving_url.replace('http://localhost:8080/_ah', '/_ah') + '=s400'
        } else {
          return rec.serving_url + '=s400'
        }
      } else {
        return '/static/broken.svg'
      }
    }
  },
  directives: {
    infiniteScroll
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.md-app {
  height: 1200px;
}
.grid {
  margin: -16px -16px 0 0;
  // &:after {
  //   content: '';
  //   display: block;
  //   clear: both;
  // }
}
.grid-sizer, .grid-item {
  margin-bottom: 16px;
  width: calc(100% / 4 - 16px);
  @media (max-width: 600px) {
    width: calc(100% - 16px);
  }
  @media (max-width: 960px) {
    width: calc(100% / 2 - 16px);
  }
  @media (max-width: 1280px) {
    width: calc(100% / 3 - 16px);
  }
}
.gutter-sizer {
  width: 16px;
}
</style>
