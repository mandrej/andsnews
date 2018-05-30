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
          <v-btn color="secondary" flat @click="dialog = false">Close</v-btn>
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
          <v-btn color="error" @click="agree">Yes</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="confirm = false">No</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-layout>
      <v-flex>
        <v-card tile flat>
          <v-container fluid grid-list-lg>
            <v-layout row wrap>
              <v-flex xs12 sm6 md4 lg3 xl3
                v-for="item in objects"
                :key="item.safekey">
                <div :id="`${item.safekey}`">
                  <v-card tile>
                    <v-card-media
                      v-lazy:background-image="getImgSrc(item, 's')"
                      @click="showDetail(item)"
                      style="background-position: 50% 50%"
                      height="300px">
                    </v-card-media>
                    <v-card-title primary-title>
                      <div>
                        <h3 class="title mb-0">{{item.headline}}</h3>
                        <div>{{dateFormat(item)}}</div>
                      </div>
                    </v-card-title>
                    <v-card-actions v-if="user.isAuthorized">
                      <v-btn v-if="user.isAdmin" small flat @click="removeRecord(item)">Delete</v-btn>
                      <v-spacer></v-spacer>
                      <v-btn small flat @click="showEditdForm(item)">Edit</v-btn>
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
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import VueLazyload from 'vue-lazyload'
import Edit from './Edit'
import common from '../../helpers/mixins'
import { EventBus } from '../../helpers/event-bus'
import * as easings from 'vuetify/es5/util/easing-patterns'

Vue.use(VueLazyload, {
  attempt: 1
})

export default {
  name: 'Home',
  components: {
    Edit
  },
  mixins: [ common ],
  data: () => ({
    // size: 'lg', v-bind="{[`grid-list-${size}`]: true}"
    bottom: false,
    distance: 800,

    dialog: false,
    confirm: false,
    editForm: false,

    options: {
      duration: 300,
      offset: -16,
      easings: Object.keys(easings)
    }
  }),
  computed: {
    ...mapState(['user', 'current', 'objects', 'pages', 'next', 'page', 'filter', 'busy'])
  },
  created () {
    window.addEventListener('scroll', () => {
      this.bottom = this.bottomVisible()
    })
    this.loadMore()
  },
  mounted () {
    EventBus.$on('goto', () => {
      setTimeout(() => {
        this.$vuetify.goTo('#' + this.current.safekey, this.options)
      }, 50)
    })
  },
  updated () {
    this.bottom = false
  },
  watch: {
    // https://scotch.io/tutorials/simple-asynchronous-infinite-scroll-with-vue-watchers
    bottom (val, oldVal) {
      if (val) {
        this.loadMore()
      }
    }
  },
  methods: {
    bottomVisible () {
      const scrollY = window.scrollY
      const visible = document.documentElement.clientHeight
      const pageHeight = document.documentElement.scrollHeight
      return visible + scrollY + this.distance >= pageHeight
    },
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
