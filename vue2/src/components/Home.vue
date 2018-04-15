<template>
  <div class="page-container">
    <v-btn id="add" v-if="user.isAuthorized" fab medium color="warning" class="secondary--text" @click="$router.push({name: 'add'})">
      <v-icon>add</v-icon>
    </v-btn>

    <!-- <v-dialog v-model="dialog" max-width="400px">
      <v-card>
        <v-card-title class="headline">
          No photos for current filter / search
        </v-card-title>
        <v-card-actions>
          <v-btn color="primary" flat @click.stop="dialog=false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog> -->

    <v-app light>
      <v-toolbar app>
        <v-toolbar-title>{{title}}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon :to="{ name: 'find' }">
          <v-icon>search</v-icon>
        </v-btn>
        <SignIn></SignIn>
      </v-toolbar>

      <v-content>
        <div id="scrolling-techniques"
          v-infinite-scroll="loadMore"
          infinite-scroll-disabled="stopLoading"
          infinite-scroll-distance="distance">
          <div class="grid">
            <div
              v-masonry
              transition-duration="0.5s"
              item-selector=".grid-item"
              horizontal-order="true"
              column-width=".grid-sizer"
              gutter=".gutter-sizer">
              <div class="grid-sizer"></div>
              <div class="gutter-sizer"></div>
              <div v-masonry-tile class="grid-item" v-for="item in objects" :key="item.safekey">
                <v-card>
                  <v-card-media>
                    <router-link :to="{ name: 'item', params: { id: item.safekey }}">
                      <img :src="src(item)" :alt="item.slug">
                    </router-link>
                  </v-card-media>
                  <v-card-title primary-title>
                    <div>
                      <h3 class="headline mb-0">{{item.headline}}</h3>
                      <div>{{item.date}}</div>
                    </div>
                  </v-card-title>
                  <v-card-actions>
                    <v-layout justify-space-between v-if="user.isAuthorized">
                      <v-btn v-if="user.isAdmin" flat color="secondary" @click="deleteRecord(item)">Delete</v-btn>
                      <v-btn flat color="primary" :to="{ name: 'edit', params: { id: item.safekey }}">Edit</v-btn>
                    </v-layout>
                  </v-card-actions>
                </v-card>
              </div>
            </div>
          </div>
        </div>
      </v-content>
    </v-app>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import { VueMasonryPlugin } from 'vue-masonry'
import infiniteScroll from 'vue-infinite-scroll'
import SignIn from './SignIn'

Vue.use(VueMasonryPlugin, infiniteScroll)

export default {
  name: 'Home',
  components: {
    SignIn
  },
  data: () => ({
    title: 'ANDрејевићи',
    distance: 1200
  }),
  created () {
    this.$store.dispatch('loadList')
  },
  computed: {
    ...mapState(['user', 'objects', 'page', 'next', 'loading']),
    stopLoading () { // if true
      return this.loading || this.objects.length === 0
    }
  },
  methods: {
    loadMore () {
      if (this.next || this.objects.length === 0) {
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
#add {
  position: fixed;
  bottom: 16px;
  right: 32px;
  z-index: 10;
}
.grid {
  margin: 0;
  padding: 16px;
  padding-right: 0;
}
.grid-sizer, .grid-item {
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
.grid-item {
  margin-bottom: 16px;
}
.gutter-sizer {
  width: 16px;
}
</style>
