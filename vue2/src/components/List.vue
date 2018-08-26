<template>
  <div>
    <Edit :visible="editForm" @close="editForm = false"></Edit>

    <v-dialog v-model="confirm" max-width="300px" persistent lazy>
      <v-card>
        <v-card-title class="headline warning" primary-title>
          Are you sure?
        </v-card-title>
        <v-card-text>
          you want to delete "{{current.headline}}"
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-3">
          <v-layout justify-space-between row>
            <v-btn color="error" @click="agree">Yes</v-btn>
            <v-btn color="secondary" @click="confirm = false">No</v-btn>
          </v-layout>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-container fluid grid-list-lg>
      <viewer :options="viewerOptions" :images="objects">
        <template slot-scope="scope">
          <v-layout row wrap>
            <v-flex xs12 sm6 md4 lg3 xl2
              v-for="item in scope.images"
              :key="item.safekey">
              <v-card light>
                <v-card-media style="cursor: pointer">
                  <img
                    v-lazy="getImgSrc(item, 's')"
                    :data-full="getImgSrc(item)">
                </v-card-media>
                <v-card-title>
                  <span class="title">{{item.headline}}</span>
                </v-card-title>
                <v-card-actions class="pa-3">
                  <v-layout justify-end row>
                    <v-btn v-if="user.isAdmin" icon flat color="primary" @click="removeRecord(item)">
                      <v-icon>cancel</v-icon>
                    </v-btn>
                    <v-btn v-if="user.isAuthorized" icon flat color="primary" @click="showEditdForm(item)">
                      <v-icon>edit</v-icon>
                    </v-btn>
                    <v-btn icon flat color="primary" :href="`/api/download/${item.safekey}`" :download="`${item.slug}.jpg`" target="_blank">
                      <v-icon>file_download</v-icon>
                    </v-btn>
                  </v-layout>
                </v-card-actions>
              </v-card>
            </v-flex>
          </v-layout>
        </template>
      </viewer>
    </v-container>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import VueLazyload from 'vue-lazyload'
import common from '@/helpers/mixins'
import 'viewerjs/dist/viewer.css'
import Viewer from 'v-viewer'

Vue.use(VueLazyload, {
  attempt: 1
})
Vue.use(Viewer, {
  debug: true
})

export default {
  name: 'List',
  components: {
    'Edit': () => import(/* webpackChunkName: "edit" */ './Edit')
  },
  mixins: [ common ],
  data: () => ({
    // size: 'lg', v-bind="{[`grid-list-${size}`]: true}"
    bottom: false,
    distance: 800,
    confirm: false,
    editForm: false,
    viewerOptions: {
      loop: false,
      title: false,
      navbar: false,
      keyborad: false,
      toolbar: false,
      rotatable: false,
      url: 'data-full'
    }
  }),
  computed: {
    ...mapState('All', ['user', 'current', 'objects', 'pages', 'next', 'page'])
  },
  created () {
    window.addEventListener('scroll', () => {
      this.bottom = this.bottomVisible()
    })
    this.loadMore()
  },
  updated () {
    this.bottom = false
  },
  watch: {
    // https://scotch.io/tutorials/simple-asynchronous-infinite-scroll-with-vue-watchers
    bottom (val) {
      if (val) {
        this.loadMore()
      }
    }
  },
  methods: {
    // console.log(this.$vuetify.breakpoint.xs)
    bottomVisible () {
      const scrollY = window.scrollY
      const visible = document.documentElement.clientHeight
      const pageHeight = document.documentElement.scrollHeight
      return visible + scrollY + this.distance >= pageHeight
    },
    loadMore () {
      if (this.objects.length === 0) {
        this.$store.dispatch('All/fetchRecords')
      } else if (this.next && this.pages.indexOf(this.next) === -1) {
        this.$store.dispatch('All/fetchRecords', this.next)
      }
    },
    showEditdForm (rec) {
      this.$store.dispatch('All/changeCurrent', rec)
      this.editForm = true
    },
    removeRecord (rec) {
      this.$store.dispatch('All/changeCurrent', rec)
      this.confirm = true
    },
    agree () {
      this.$store.dispatch('All/deleteRecord', this.current)
      this.confirm = false
    }
  }
}
</script>

<style lang="scss" scoped>
.v-card__media {
  img {
    opacity: 0;
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    &[lazy=loaded] {
      opacity: 1;
    }
  }
}
</style>

<style>
.viewer-backdrop {
  background-color: white;
}
</style>
