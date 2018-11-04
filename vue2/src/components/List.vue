<template>
  <div>
    <Edit :visible="editForm" :rec="current" @close="editForm = false"></Edit>

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
      <Photoswipe>
        <masonry
          :cols="{default: 6, 1440: 4, 1024: 3, 960: 2, 600: 1}" :gutter="16">
          <v-card light class="card"
            v-for="item in objects" :key="item.safekey">
            <img
              :title="item.headline"
              :src="getImgSrc(item, '400')"
              :data-pswp-src="getImgSrc(item)">
            <v-card-title primary-title class="pt-3">
              <div>
                <h3 class="title">{{item.headline}}</h3>
                <div>{{dateFormat(item)}}</div>
                <div>{{item.author.match(/[^@]+/)[0]}}</div>
              </div>
            </v-card-title>
            <v-card-actions class="pt-0 px-3 pb-3">
              <v-layout justify-end row>
                <v-btn v-if="canDelete(user)" icon flat color="primary" @click.native="removeRecord(item)">
                  <v-icon>cancel</v-icon>
                </v-btn>
                <v-btn v-if="canEdit(user)" icon flat color="primary" @click.native="showEditdForm(item)">
                  <v-icon>edit</v-icon>
                </v-btn>
                <v-btn icon flat color="primary" :href="`/api/download/${item.safekey}`" :download="`${item.slug}.jpg`" target="_blank">
                  <v-icon>file_download</v-icon>
                </v-btn>
              </v-layout>
            </v-card-actions>
          </v-card>
        </masonry>
      </Photoswipe>
    </v-container>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import VueMasonry from 'vue-masonry-css'
import Photoswipe from 'vue-pswipe'
import common from '@/helpers/mixins'
import * as easings from 'vuetify/es5/util/easing-patterns'

Vue.use(VueMasonry)
Vue.use(Photoswipe, {
  preload: [1,1],
  history: false,
  shareEl: false,
})

export default {
  name: 'List',
  components: {
    'Edit': () => import(/* webpackChunkName: "edit" */ './Edit')
  },
  mixins: [ common ],
  data: () => ({
    bottom: false,
    distance: 1800,
    confirm: false,
    current: {},
    editForm: false,
    index: 0,
    scrollOptions: {
      duration: 300,
      offset: -144,
      easings: Object.keys(easings)
    }
  }),
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('app', ['objects', 'next'])
  },
  created () {
    window.addEventListener('scroll', () => {
      this.bottom = this.bottomVisible()
    })
  },
  mounted () {
    window.addEventListener('hide', () => {
      const elm = document.querySelectorAll('.card')[this.index]
      setTimeout(() => {
        this.$vuetify.goTo(elm, this.scrollOptions)
      }, 350)
    })
    window.addEventListener('view', event => {
      this.index = event.detail.index
    })
  },
  updated () {
    this.bottom = false
  },
  watch: {
    // https://scotch.io/tutorials/simple-asynchronous-infinite-scroll-with-vue-watchers
    bottom (val) {
      if (val && this.next) {
        this.$store.dispatch('app/fetchRecords')
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
    canEdit (user) {
      return user.isAuthorized
    },
    showEditdForm (rec) {
      this.current = rec
      this.editForm = true
    },
    canDelete (user) {
      return user.isAdmin
    },
    removeRecord (rec) {
      this.current = rec
      this.confirm = true
    },
    agree () {
      this.$store.dispatch('app/deleteRecord', this.current)
      this.confirm = false
    }
  }
}
</script>

<style lang="scss" scoped>
.card {
  margin-bottom: 16px;
  img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    cursor: pointer;
  }
}
</style>
