<template>
  <div class="page-container">
    <md-button id="add" class="md-icon-button md-raised md-accent md-size-2x" @click="$router.push({name: 'add'})">
      <md-icon>add</md-icon>
    </md-button>

    <md-app md-mode="reveal">
      <md-app-toolbar class="md-primary">
        <span class="md-title">{{title}}</span>
      </md-app-toolbar>

      <md-app-content>
        <div v-infinite-scroll="loadMore" infinite-scroll-disabled="loading" infinite-scroll-distance="distance">
          <div class="grid">
            <div v-masonry transition-duration="0.5s" item-selector=".grid-item"
              horizontal-order="true" column-width=".grid-sizer" gutter=".gutter-sizer">
              <div class="grid-sizer"></div>
              <div class="gutter-sizer"></div>
              <div v-masonry-tile class="grid-item" v-for="item in objects" :key="item.safekey">
                <md-card>
                  <md-card-media>
                    <router-link :to="{ name: 'item', params: { id: item.safekey }}">
                      <img :src="src(item)" :alt="item.slug">
                    </router-link>
                  </md-card-media>
                  <md-card-header>
                    <div class="md-title">{{item.headline}}</div>
                    <div class="md-subhead">{{item.date}}</div>
                  </md-card-header>
                  <md-card-actions>
                    <md-button class="md-primary" @click="deleteRecord(item)">Delete</md-button>
                    <router-link :to="{ name: 'edit', params: { id: item.safekey }}">
                      <md-button class="md-primary">Edit</md-button>
                    </router-link>
                  </md-card-actions>
                </md-card>
              </div>
            </div>
          </div>
        </div>
      </md-app-content>
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
  data: () => ({
    title: 'ANDрејевићи',
    distance: 1200
  }),
  computed: {
    ...mapState(['objects', 'page', 'next', 'loading'])
  },
  methods: {
    loadMore () {
      if (this.objects.length === 0 || this.next) {
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
    },
    deleteRecord (rec) {
      this.$store.dispatch('deleteRecord', rec)
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
  height: 100vh;
}
#add {
  position: absolute;
  bottom: 16px;
  right: 32px;
  z-index: 10;
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
  @media (max-width: 1280px) {
    width: calc(100% / 3 - 16px);
  }
  @media (max-width: 960px) {
    width: calc(100% / 2 - 16px);
  }
  @media (max-width: 600px) {
    width: calc(100% - 16px);
  }
}
.gutter-sizer {
  width: 16px;
}
.md-card {
  margin: 0;
}
</style>
