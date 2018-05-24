<template>
  <div>
    <Edit :visible="editForm" @close="editForm = false"></Edit>
    <Info :visible="showInfo" @close="showInfo = false"></Info>
    <!-- <v-progress-linear :indeterminate="true" height="2"></v-progress-linear> -->

    <v-app light>
      <v-toolbar app flat>
        <v-btn icon  @click="back">
          <v-icon>arrow_back</v-icon>
        </v-btn>
        <v-toolbar-title class="headline">{{current.headline || 'Not found'}}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn v-if="user.isAuthorized" icon @click="editForm = true" flat>
          <v-icon>create</v-icon>
        </v-btn>
        <v-btn icon :href="`/api/download/${current.safekey}`" :download="`${current.slug}.jpg`" target="_blank" flat>
          <v-icon>file_download</v-icon>
        </v-btn>
        <v-btn icon @click="showInfo = true" flat>
          <v-icon>more_vert</v-icon>
        </v-btn>
      </v-toolbar>

      <v-content>
        <v-progress-circular v-if="isLoading"
          indeterminate
          :size="100"
          :width="5"
          color="black"></v-progress-circular>
        <v-carousel :cycle="false" light
          v-bind="current"
          :value="index"
          @input="currentIndex"
          hide-delimiters lazy>
          <v-carousel-item v-for="item in objects" :key="item.safekey"
            v-lazy:background-image="getImgSrc(item)"
            style="background-size: contain; background-position: 50% 50%">
          </v-carousel-item>
        </v-carousel>
      </v-content>
    </v-app>
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
  props: ['id'],
  data: () => ({
    showInfo: false,
    editForm: false,
    isLoading: false
  }),
  computed: {
    ...mapState(['user', 'current', 'objects', 'pages', 'next', 'page', 'filter', 'busy']),
    index () {
      return this.objects.findIndex(item => item.safekey === this.id)
    }
  },
  mounted () {
    this.$Lazyload.$on('loading', this.loading)
    this.$Lazyload.$on('loaded', this.loading)
  },
  methods: {
    currentIndex (idx) {
      const obj = this.objects[idx]
      this.$store.dispatch('changeCurrent', obj)
      this.$router.push({name: 'item', params: {id: obj.safekey}})
      if ((this.objects.length - idx) === 3) this.loadMore()
    },
    loadMore () {
      if (this.objects.length === 0) {
        this.$store.dispatch('fetchRecords')
      } else if (this.next && this.pages.indexOf(this.next) === -1) {
        this.$store.dispatch('fetchRecords', this.next)
      }
    },
    loading (e) {
      this.isLoading = !e.state.loaded
    },
    back () {
      EventBus.$emit('scroll')
      this.$router.push({name: 'home'})
    }
  }
}
</script>

<style lang="scss" scoped>
.progress-circular {
  position: absolute;
  top: calc(50% - 50px);
  left: calc(50% - 50px)
}
.carousel {
  height: calc(100vh - 56px);
}
</style>
