<template>
  <div>
    <Info :visible="showInfo" @close="showInfo = false"></Info>

    <v-dialog
      v-model="show"
      lazy fullscreen hide-overlay scrollable
      transition="dialog-bottom-transition">
      <v-card tile flat>
        <v-toolbar dark color="secondary" class="aperture">
          <v-btn icon @click="close">
            <v-icon>close</v-icon>
          </v-btn>
          <v-toolbar-title class="headline">{{current.headline || 'Not found'}}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon @click="showInfo = true" flat>
            <v-icon>more_vert</v-icon>
          </v-btn>
        </v-toolbar>
        <v-card-media>
          <v-progress-circular v-if="isLoading"
            indeterminate
            :size="100"
            :width="5"
            color="secondary"></v-progress-circular>
          <v-carousel light
            :cycle="false"
            :value="index"
            @input="currentIndex"
            hide-delimiters>
            <v-carousel-item v-for="item in objects" :key="item.safekey"
              v-lazy:background-image="getImgSrc(item)" class="slide">
            </v-carousel-item>
          </v-carousel>
        </v-card-media>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import VueLazyload from 'vue-lazyload'
import common from '@/helpers/mixins'
import { EventBus } from '@/helpers/event-bus'

Vue.use(VueLazyload)

export default {
  name: 'Item',
  components: {
    'Info': () => import(/* webpackChunkName: "info" */ './Info')
  },
  mixins: [ common ],
  props: ['visible', 'index'],
  data: () => ({
    showInfo: false,
    isLoading: false
  }),
  computed: {
    ...mapState('All', ['current', 'objects', 'pages', 'next', 'page'])
  },
  mounted () {
    this.$Lazyload.$on('loading', this.loading)
    this.$Lazyload.$on('loaded', this.loading)
  },
  methods: {
    currentIndex (idx) {
      const obj = this.objects[idx]
      this.$store.dispatch('All/changeCurrent', obj)
      if ((this.objects.length - idx) === 4) this.loadMore()
    },
    loadMore () {
      if (this.objects.length === 0) {
        this.$store.dispatch('All/fetchRecords')
      } else if (this.next && this.pages.indexOf(this.next) === -1) {
        this.$store.dispatch('All/fetchRecords', this.next)
      }
    },
    loading (event) {
      this.isLoading = !event.state.loaded
    },
    close () {
      this.show = false
      EventBus.$emit('goto')
    }
  }
}
</script>

<style scoped>
.v-carousel {
  height: calc(100vh - 64px);
}
.v-progress-circular {
  position: absolute;
  top: calc(50% - 23px);
  left: calc(50% - 46px);
}
.slide {
  background-size: contain;
  background-position: 50% 50%;
}
</style>
