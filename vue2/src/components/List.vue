<template>
  <div>
    <Item :visible="showItem" :index="index" @close="showItem = false"></Item>
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

    <v-card tile flat>
      <v-container fluid grid-list-lg>
        <v-layout row wrap>
          <v-flex xs12 sm6 md4 lg3 xl2
            v-for="(item, idx) in objects"
            :key="item.safekey">
            <div :id="`${item.safekey}`" class="square elevation-1">
              <img v-lazy="getImgSrc(item, 's')" @click="showDetail(item, idx)">
              <div class="px-3 pt-3">
                <h3 class="title mb-0">{{item.headline}}</h3>
                <div>{{dateFormat(item)}}</div>
              </div>
              <v-layout justify-center pb-3>
                <v-btn v-if="user.isAdmin" small flat @click="removeRecord(item)">Delete</v-btn>
                <v-spacer></v-spacer>
                <v-btn small flat @click="showEditdForm(item)">Edit</v-btn>
              </v-layout>
            </div>
          </v-flex>
        </v-layout>
      </v-container>
    </v-card>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import VueLazyload from 'vue-lazyload'
import Item from './Item'
import Edit from './Edit'
import common from '@/helpers/mixins'
import { EventBus } from '@/helpers/event-bus'
import * as easings from 'vuetify/es5/util/easing-patterns'

Vue.use(VueLazyload, {
  attempt: 1
})

export default {
  name: 'Home',
  components: {
    Item,
    Edit
  },
  mixins: [ common ],
  data: () => ({
    // size: 'lg', v-bind="{[`grid-list-${size}`]: true}"
    index: null,

    bottom: false,
    distance: 800,

    dialog: false,
    confirm: false,
    editForm: false,
    showItem: false,

    options: {
      duration: 300,
      offset: -16,
      easings: Object.keys(easings)
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
</style>
