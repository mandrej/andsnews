<template>
  <div>
    <Item :visible="showItem" :index="index" @close="showItem = false"></Item>
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
      <v-layout row wrap>
        <v-flex xs12 sm6 md4 lg3 xl2
          v-for="(item, idx) in objects"
          :key="item.safekey">
          <v-card light :id="`${item.safekey}`">
            <v-card-media
              @click="showDetail(item, idx)"
              class="white--text"
              style="cursor: pointer"
              height="300px"
              v-lazy:background-image="getImgSrc(item, 's')">
              <v-container fill-height fluid>
                <v-layout fill-height>
                  <v-flex xs12 align-end flexbox>
                    <span class="headline">{{item.headline}}</span><br>
                    <span>{{dateFormat(item)}}</span>
                  </v-flex>
                </v-layout>
              </v-container>
            </v-card-media>
            <v-card-actions class="pa-3">
              <v-layout justify-space-between row>
                <v-btn icon flat color="error" @click="removeRecord(item)">
                  <v-icon>cancel</v-icon>
                </v-btn>
                <v-btn icon flat color="secondary" @click="showEditdForm(item)">
                  <v-icon>edit</v-icon>
                </v-btn>
                <v-btn icon flat color="secondary" :href="`/api/download/${item.safekey}`" :download="`${item.slug}.jpg`" target="_blank">
                  <v-icon>file_download</v-icon>
                </v-btn>
              </v-layout>
            </v-card-actions>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import VueLazyload from 'vue-lazyload'
import common from '@/helpers/mixins'
import { EventBus } from '@/helpers/event-bus'
import * as easings from 'vuetify/es5/util/easing-patterns'

Vue.use(VueLazyload, {
  attempt: 1
})

export default {
  name: 'List',
  components: {
    'Item': () => import(/* webpackChunkName: "item" */ './Item'),
    'Edit': () => import(/* webpackChunkName: "edit" */ './Edit')
  },
  mixins: [ common ],
  data: () => ({
    // size: 'lg', v-bind="{[`grid-list-${size}`]: true}"

    bottom: false,
    distance: 800,
    index: null,
    confirm: false,
    editForm: false,
    showItem: false,
    options: {
      duration: 300,
      offset: -144,
      easings: Object.keys(easings)
    }
  }),
  computed: {
    ...mapState('All', ['current', 'objects', 'pages', 'next', 'page'])
  },
  created () {
    window.addEventListener('scroll', () => {
      this.bottom = this.bottomVisible()
    })
    this.loadMore()
  },
  mounted () {
    EventBus.$on('goto', () => {
      this.$vuetify.goTo('#' + this.current.safekey, this.options)
    })
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
    showDetail (rec, idx) {
      this.$store.dispatch('All/changeCurrent', rec)
      this.index = idx
      this.showItem = true
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
.v-card__media {
  opacity: 0;
  background-position: center;
  transition: all 0.3s ease-in;
  &[lazy=loaded] {
    opacity: 1;
  }
}
</style>
