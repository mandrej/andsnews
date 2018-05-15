<template>
  <div>
    <Edit :visible="editForm" @close="editForm = false"></Edit>

    <v-dialog v-model="dialog" max-width="300px" lazy>
      <v-card>
        <v-card-title class="headline">
          No photos<br>
          <small>for current filter / search</small>
        </v-card-title>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" flat @click.native="dialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirm" max-width="300px" persistent lazy>
      <v-card>
        <v-card-title class="headline">
          Are you sure?<br>
          <small>you want to delete "{{current.headline}}"</small>
        </v-card-title>
        <v-card-actions>
          <v-btn color="error" @click.native="agree">Yes</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click.native="confirm = false">No</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <div v-infinite-scroll="loadMore"
      infinite-scroll-disabled="disabled"
      infinite-scroll-distance="distance">
      <v-layout>
        <v-flex>
          <v-card>
            <v-container fluid grid-list-lg>
              <v-layout row wrap>
                <v-flex xs12 sm6 md4 lg3 xl2
                  v-for="item in objects"
                  :key="item.safekey">
                  <div :id="`${item.safekey}`">
                    <v-card flat tile>
                      <v-card-title class="title" primary-title>
                        {{item.headline}}
                      </v-card-title>
                      <v-card-media
                        v-lazy:background-image="getImgSrc(item, 's')"
                        @click="showDetail(item)"
                        style="background-position: 50% 50%"
                        height="300px">
                      </v-card-media>
                      <v-card-actions v-if="user.isAuthorized">
                        <v-btn v-if="user.isAdmin" flat class="black--text" @click="removeRecord(item)">Delete</v-btn>
                        <v-spacer style="text-align: center">{{dateFormat(item, 'short')}}</v-spacer>
                        <v-btn flat class="black--text" @click="showEditdForm(item)">Edit</v-btn>
                      </v-card-actions>
                    </v-card>
                  </div>
                </v-flex>
              </v-layout>
            </v-container>
          </v-card>
        </v-flex>
      </v-layout>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import VueLazyload from 'vue-lazyload'
import infiniteScroll from 'vue-infinite-scroll'
import Edit from './Edit'
import common from '../../helpers/mixins'
import { EventBus } from '../../helpers/event-bus'
import * as easings from 'vuetify/es5/util/easing-patterns'

Vue.use(VueLazyload, {
  preLoad: 2,
  attempt: 1
})

export default {
  name: 'Home',
  components: {
    Edit
  },
  directives: {
    infiniteScroll
  },
  mixins: [ common ],
  data: () => ({
    // size: 'lg', v-bind="{[`grid-list-${size}`]: true}"
    distance: 800,
    dialog: false,
    stop: false,
    confirm: false,
    editForm: false,

    duration: 300,
    offset: -16,
    easing: 'easeInOutCubic',
    easings: Object.keys(easings)
  }),
  computed: {
    ...mapState(['user', 'current', 'objects', 'pages', 'next', 'filter', 'busy']),
    options () {
      return {
        duration: this.duration,
        offset: this.offset,
        easing: this.easing
      }
    },
    disabled () {
      return this.busy || this.stop
    }
  },
  mounted () {
    EventBus.$on('reload', () => {
      this.$store.dispatch('fetchRecords')
    })
    EventBus.$on('scroll', () => {
      setTimeout(() => {
        this.$vuetify.goTo('#' + this.current.safekey, this.options)
      }, 50)
    })
  },
  watch: {
    busy (newVal, oldVal) {
      if (!newVal && this.objects.length === 0) {
        this.stop = true
        this.dialog = true
      } else {
        this.stop = false
      }
    }
  },
  methods: {
    loadMore () {
      if (this.objects.length === 0) {
        this.$store.dispatch('fetchRecords')
      } else if (this.next && this.pages.indexOf(this.next) === -1) {
        this.$store.dispatch('fetchRecords', this.next)
      }
    },
    showDetail (rec) {
      this.$store.dispatch('changeCurrent', rec)
      this.$router.push({name: 'item', params: {id: rec.safekey}})
    },
    showEditdForm (rec) {
      this.$store.dispatch('changeCurrent', rec)
      this.editForm = true
    },
    removeRecord (rec) {
      this.$store.dispatch('changeCurrent', rec)
      this.confirm = true
    },
    agree () {
      this.$store.dispatch('deleteRecord', this.current)
      this.confirm = false
    }
  }
}
</script>
