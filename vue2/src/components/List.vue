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
          <v-btn color="error" @click="agree">Yes</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="confirm = false">No</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-container fluid grid-list-lg>
      <viewer :options="viewerOptions" :images="objects"
        class="viewer" ref="viewer">
        <template slot-scope="scope">
          <v-layout row wrap>
            <v-flex xs12 sm6 md4 lg3 xl2
              v-for="item in scope.images"
              :key="item.safekey">
              <div :id="`${item.safekey}`" class="square">
                <img :alt="alt(item)"
                  v-lazy="getImgSrc(item, 's')"
                  :data-source="getImgSrc(item)">
                <v-list two-line>
                  <v-list-tile>
                    <v-list-tile-content>
                      <v-list-tile-title>{{item.headline}}</v-list-tile-title>
                      <v-list-tile-sub-title>{{dateFormat(item)}}</v-list-tile-sub-title>
                    </v-list-tile-content>
                    <v-list-tile-action>
                      <v-menu>
                        <v-btn icon slot="activator">
                          <v-icon>more_vert</v-icon>
                        </v-btn>
                        <v-list>
                          <v-list-tile @click="showEditdForm(item)">
                            <v-list-tile-content>Edit</v-list-tile-content>
                          </v-list-tile>
                          <v-list-tile :href="`/api/download/${item.safekey}`" :download="`${item.slug}.jpg`" target="_blank">
                            <v-list-tile-content>Download</v-list-tile-content>
                          </v-list-tile>
                          <v-list-tile v-if="user.isAdmin" @click="removeRecord(item)">
                            <v-list-tile-content>Delete</v-list-tile-content>
                          </v-list-tile>
                        </v-list>
                      </v-menu>
                    </v-list-tile-action>
                  </v-list-tile>
                </v-list>
              </div>
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
import 'viewerjs/dist/viewer.css'
import Viewer from 'v-viewer'
import common from '@/helpers/mixins'
// import * as easings from 'vuetify/es5/util/easing-patterns'

Vue.use(VueLazyload, {
  attempt: 1
})
Vue.use(Viewer)

export default {
  name: 'Home',
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
      title: true,
      toolbar: false,
      tooltip: true,
      rotatable: false,
      scalable: false,
      transition: true,
      fullscreen: true,
      keyboard: true,
      url: 'data-source'
    }
  }),
  computed: {
    ...mapState('All', ['user', 'current', 'objects', 'pages', 'next', 'page', 'filter', 'busy'])
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
    alt (rec) {
      return `${rec.aperture ? 'f/' + rec.aperture : ''}` +
        ` ${rec.shutter ? rec.shutter + 's' : ''}` +
        ` ${rec.iso ? rec.iso + ' ASA' : ''}` +
        ` ${rec.model ? rec.model : ''} ${rec.lens ? rec.lens : ''}` +
        ` ${rec.focal_length ? '(' + rec.focal_length + 'mm)' : ''}`
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
.square {
  margin-bottom: 8px;
  img {
    max-width: 100%;
    opacity: 0;
    transition: all 0.5s ease-in;
    &[lazy=loaded] {
      opacity: 1;
    }
  }
}
.v-list__tile__title {
  font-size: 20px;
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
    color: rgba(0, 0, 0, 0.87);
    font-family: 'Roboto', Helvetica, Arial, sans-serif !important;
    font-size: 16px;
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
.viewer-button {
  background-color: rgba(0, 0, 0, 0.87);
}
.viewer-backdrop {
  background-color: #fff;
}
</style>
