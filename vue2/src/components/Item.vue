<template>
  <div>
    <Edit :visible="editForm" @close="editForm = false"></Edit>
    <Info :visible="showInfo" @close="showInfo = false"></Info>

    <v-dialog
      v-model="show"
      lazy
      fullscreen
      transition="scale-transition"
      hide-overlay
      scrollable>
      <v-card tile light>
        <v-toolbar card>
          <v-btn icon @click.native="close">
            <v-icon>close</v-icon>
          </v-btn>
          <v-toolbar-title>{{current.headline || 'Not found'}}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn v-if="user.isAuthorized" icon @click="editForm = true" flat>
            <v-icon>create</v-icon>
          </v-btn>
          <v-btn icon :href="`/api/download/${current.safekey}`" flat>
            <v-icon>file_download</v-icon>
          </v-btn>
          <v-btn icon @click="showInfo = true" flat>
            <v-icon>more_vert</v-icon>
          </v-btn>
        </v-toolbar>
        <v-card-media>
          <v-carousel v-if="show" :cycle="false" light
            :value="index"
            @input="currentIndex"
            hide-delimiters lazy>
            <v-carousel-item v-for="item in objects" :key="item.safekey"
              v-lazy:background-image="getImgSrc(item)"
              style="background-size: contain; background-position: 50% 50%">
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
import common from '../../helpers/mixins'
import Edit from './Edit'
import Info from './Info'
import { EventBus } from '../../helpers/event-bus'

Vue.use(VueLazyload)

export default {
  name: 'Item',
  components: {
    Info,
    Edit
  },
  mixins: [ common ],
  props: ['visible'],
  data: () => ({
    showInfo: false,
    editForm: false
  }),
  computed: {
    ...mapState(['user', 'current', 'index', 'objects', 'pages', 'next', 'filter', 'busy'])
  },
  methods: {
    currentIndex (idx) {
      this.$store.dispatch('changeCurrent', this.objects[idx])
      if ((this.objects.length - idx) === 3) this.loadMore()
    },
    loadMore () {
      if (this.objects.length === 0) {
        this.$store.dispatch('fetchRecords')
      } else if (this.next && this.pages.indexOf(this.next) === -1) {
        this.$store.dispatch('fetchRecords', this.next)
      }
    },
    close () {
      EventBus.$emit('scroll')
      this.show = false
    }
  }
}
</script>

<style lang="scss" scoped>
.carousel {
  height: calc(100vh - 56px);
}
</style>
