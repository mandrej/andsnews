<template>
  <div>
    <Edit :visible="editForm" @close="editForm = false"></Edit>
    <Item :visible="showItem" :index="idx" @close="showItem = false"></Item>

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
          <v-btn color="primary" @click.native="agree">Yes</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click.native="confirm = false">No</v-btn>
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
                  v-for="(item, idx) in objects"
                  :key="item.safekey">
                  <v-card tile>
                    <v-card-title class="title" primary-title>
                      {{item.headline}}
                    </v-card-title>
                    <v-card-media
                      v-lazy:background-image="getImgSrc(item, 's')"
                      @click="showDetail(item, idx)"
                      style="background-position: 50% 50%"
                      height="300px">
                    </v-card-media>
                    <v-card-actions v-if="user.isAuthorized">
                      <v-btn v-if="user.isAdmin" flat color="secondary" @click="removeRecord(item)">Delete</v-btn>
                      <v-spacer style="text-align: center">{{dateFormat(item, 'short')}}</v-spacer>
                      <v-btn flat color="primary" @click="showEditdForm(item)">Edit</v-btn>
                    </v-card-actions>
                  </v-card>
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
import Item from './Item'
import Edit from './Edit'
import common from '../../helpers/mixins'

Vue.use(VueLazyload)

export default {
  name: 'Home',
  components: {
    Item,
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
    idx: 0,
    showItem: false,
    editForm: false
  }),
  computed: {
    ...mapState(['user', 'current', 'objects', 'pages', 'next', 'filter', 'busy']),
    disabled () {
      return this.busy || this.stop
    }
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
    showDetail (rec, idx) {
      this.$store.dispatch('changeCurrent', rec)
      this.idx = idx
      this.showItem = true
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
