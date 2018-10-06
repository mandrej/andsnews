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
              <v-card light class="card">
                <img :alt="alt(item)"
                  v-lazy="getImgSrc(item, '400')"
                  :data-full="getImgSrc(item)">
                <v-card-title primary-title class="pt-3">
                  <div>
                    <h3 class="title">{{item.headline}}</h3>
                    <div>{{dateFormat(item)}}</div>
                    <div>{{item.author.match(/[^@]+/)[0]}}</div>
                  </div>
                </v-card-title>
                <v-card-actions class="pt-0 px-3 pb-3">
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
          {{scope.viewerOptions}}
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
import * as easings from 'vuetify/es5/util/easing-patterns'

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
      navbar: false,
      keyborad: false,
      toolbar: false,
      rotatable: false,
      url: 'data-full'
    },
    index: 0,
    scrollOptions: {
      duration: 300,
      offset: -144,
      easings: Object.keys(easings)
    }
  }),
  computed: {
    ...mapState('All', ['user', 'current', 'objects', 'pages', 'next', 'page'])
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
      if (val) {
        this.$store.dispatch('All/fetchRecords', this.next)
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
    },
    alt (rec) {
      return `${rec.aperture ? 'f/' + rec.aperture : ''}` +
        ` ${rec.shutter ? rec.shutter + 's' : ''}` +
        ` ${rec.iso ? rec.iso + ' ASA' : ''}` +
        ` ${rec.model ? rec.model : ''} ${rec.lens ? rec.lens : ''}` +
        ` ${rec.focal_length ? '(' + rec.focal_length + 'mm)' : ''}`
    }
  }
}
</script>

<style lang="scss" scoped>
.card {
  img {
    opacity: 0;
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    cursor: pointer;
    &[lazy=loaded] {
      opacity: 1;
    }
  }
}
</style>

<style lang="scss">
.viewer-loading {
  &::after {
    animation: viewer-spinner 1s linear infinite;
    border: 8px solid rgba(0, 0, 0, .1);
    border-left-color: rgba(0, 0, 0, .5);
    border-radius: 50%;
    content: '';
    display: inline-block;
    height: 100px;
    left: 50%;
    margin-left: -50px;
    margin-top: -50px;
    position: absolute;
    top: 50%;
    width: 100px;
    z-index: 1;
  }
}
.viewer-footer {
  bottom: 10px;
  & .viewer-title {
    font-family: 'Roboto', Helvetica, Arial, sans-serif !important;
    font-size: 14px;
    line-height: normal;
    margin: 0 5% 5px;
    max-width: 90%;
    opacity: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: opacity .15s;
    white-space: nowrap;
  }
}
.viewer-backdrop {
  background-color: white;
}
</style>
