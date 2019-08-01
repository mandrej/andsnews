<template>
  <div>
    <Edit :visible="editForm" :rec="current" @close="editForm = false"></Edit>

    <v-snackbar left bottom
      v-model="snackbar"
      :timeout="timeout">
      {{ message }}
      <v-btn text icon color="white" @click="snackbar = false">
        <v-icon>close</v-icon>
      </v-btn>
    </v-snackbar>

    <v-dialog v-model="confirm" max-width="300px" persistent>
      <v-card>
        <v-card-title class="headline warning" primary-title>
          Are you sure?
        </v-card-title>
        <v-card-text>
          you want to delete "{{current.headline}}"
        </v-card-text>
        <v-card-actions class="pa-3">
          <v-container fluid>
            <v-layout justify-space-between row>
              <v-btn color="error" @click="agree">Yes</v-btn>
              <v-btn color="secondary" @click="confirm = false">No</v-btn>
            </v-layout>
          </v-container>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-container fluid grid-list-lg class="pa-3">
      <Photoswipe>
        <v-layout row wrap>
          <v-flex xs12 sm6 md4 lg3 xl2
            v-for="item in objects" :key="item.safekey">
            <v-card light class="card">
              <img
                v-lazy="getImgSrc(item, '400-c')"
                :title="caption(item)"
                :data-pswp-size="item.dim.join('x')"
                :data-pswp-src="getImgSrc(item)">
              <v-card-title>{{item.headline}}</v-card-title>
              <v-card-text>
                  <div>{{formatDate(item.date)}}</div>
                  <div>by {{item.nick}}</div>
             </v-card-text>
              <v-card-actions>
                <v-layout justify-end>
                  <v-btn v-if="canDelete(user)" icon small text color="primary" @click="removeRecord(item)">
                    <v-icon>cancel</v-icon>
                  </v-btn>
                  <v-btn v-if="canEdit(user)" icon small text color="primary" @click="showEditdForm(item)">
                    <v-icon>edit</v-icon>
                  </v-btn>
                  <v-btn icon small text color="primary" :href="`/api/download/${item.safekey}`" :download="`${item.slug}.jpg`" target="_blank">
                    <v-icon>file_download</v-icon>
                  </v-btn>
                </v-layout>
              </v-card-actions>
            </v-card>
          </v-flex>
        </v-layout>
      </Photoswipe>
    </v-container>
  </div>
</template>

<script>
import Vue from 'vue'
import { EventBus } from '@/helpers/event-bus'
import { mapState } from 'vuex'
import VueLazyload from 'vue-lazyload'
import Photoswipe from 'vue-pswipe'
import common from '@/helpers/mixins'

Vue.use(VueLazyload, {
  attempt: 1
})
Vue.use(Photoswipe, {
  preload: [1, 3],
  shareEl: false,
  addCaptionHTMLFn: function (item, captionEl, isFake) {
    if (!item.el.title) {
      captionEl.children[0].innerHTML = ''
      return false
    }
    captionEl.children[0].innerHTML = item.el.title
    return true
  }
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
    snackbar: false,
    timeout: 6000,
    message: ''
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
    EventBus.$on('delete', message => {
      this.message = message
      this.snackbar = true
    })
  },
  updated () {
    this.$nextTick(() => {
      this.bottom = false
    })
  },
  watch: {
    bottom: function (val) {
      // https://scotch.io/tutorials/simple-asynchronous-infinite-scroll-with-vue-watchers
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
    caption (rec) {
      let tmp = rec.headline
      tmp += (rec.aperture) ? ' f' + rec.aperture : ''
      tmp += (rec.shutter) ? ', ' + rec.shutter + 's' : ''
      tmp += (rec.iso) ? ', ' + rec.iso + ' ASA' : ''
      return tmp
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
  img {
    opacity: 0;
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: opacity 0.3s;
    cursor: pointer;
    &[lazy=loaded] {
      opacity: 1;
    }
  }
  .v-card__title {
    line-height: 120%;
  }
}
</style>
