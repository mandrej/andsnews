<template>
  <div>
    <Edit :visible="editForm" :rec="current" @close="editForm = false"></Edit>

    <Dialog :model="confirm" :persistent="true" title="Want to delete?" :text="current.headline">
      <v-layout justify-space-between row>
        <v-btn color="error" @click="agree">Yes</v-btn>
        <v-btn color="primary" @click="confirm = false">No</v-btn>
      </v-layout>
    </Dialog>

    <v-btn
      v-show="objects.length > 0"
      fab
      large
      fixed
      bottom
      right
      color="accent"
      style="bottom: 32px; right: 32px"
      @click="$vuetify.goTo(0, options)"
    >
      <v-icon :class="$vuetify.theme.dark ? 'white--text' : 'black--text'">arrow_upward</v-icon>
    </v-btn>

    <Photoswipe :options="pswpOptions" :key="key">
      <v-container
        fluid
        grid-list-lg
        class="pa-4"
        v-for="(list, date) in objectsByDate"
        :key="date"
      >
        <div class="text-h6 font-weight-light">{{$date(date).format('dddd, MMMM DD, YYYY')}}</div>

        <v-layout row wrap v-lazy-container="{ selector: 'img' }">
          <v-flex xs12 sm6 md4 lg3 xl2 v-for="item in list" :key="item.id">
            <v-card flat>
              <v-responsive :aspect-ratio="4/3">
                <img
                  class="lazy"
                  :data-src="getImgSrc(item, 400)"
                  :title="caption(item)"
                  :data-pswp-size="item.dim.join('x')"
                  :data-pswp-src="getImgSrc(item)"
                  :data-pswp-pid="item.id"
                />
                <p class="title">{{item.headline}}</p>
              </v-responsive>
              <v-card-text class="d-flex justify-space-between py-2">
                <div style="line-height: 28px">by {{item.nick}} at {{item.date.slice(11,)}}</div>
                <v-btn
                  v-if="item.loc"
                  icon
                  small
                  text
                  target="blank"
                  :href="'https://www.google.com/maps/search/?api=1&query=' + [...item.loc]"
                >
                  <v-icon>my_location</v-icon>
                </v-btn>
              </v-card-text>
              <template v-if="loggedIn(user)">
                <v-divider></v-divider>
                <v-card-actions class="justify-space-between">
                  <v-btn v-if="canDelete(user)" icon small text @click="removeRecord(item)">
                    <v-icon>delete</v-icon>
                  </v-btn>
                  <v-btn icon small text @click="showEditdForm(item)">
                    <v-icon>edit</v-icon>
                  </v-btn>
                  <v-btn
                    icon
                    small
                    text
                    :href="`/api/download/${item.filename}`"
                    :download="item.filename"
                  >
                    <v-icon>file_download</v-icon>
                  </v-btn>
                </v-card-actions>
              </template>
            </v-card>
          </v-flex>
        </v-layout>
      </v-container>
    </Photoswipe>

    <v-container v-if="error">
      <v-alert
        v-if="error === '0'"
        type="info"
        transition="scale-transition"
        prominent
      >No data for current filter/ search</v-alert>
      <v-alert v-else type="error" transition="scale-transition" prominent>
        Something went wrong
        <br />
        {{error}}
      </v-alert>
    </v-container>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState, mapGetters } from 'vuex'
import Photoswipe from 'vue-pswipe'
import common from '@/helpers/mixins'
import * as easings from 'vuetify/lib/services/goto/easing-patterns'

Vue.use(Photoswipe)

export default {
  name: 'List',
  components: {
    Edit: () => import(/* webpackChunkName: "edit" */ '@/components/Edit'),
    Dialog: () => import(/* webpackChunkName: "dialog" */ '@/components/Dialog')
  },
  mixins: [common],
  data: () => ({
    key: null,
    bottom: false,
    distance: 2000,
    confirm: false,
    current: {},
    editForm: false,
    options: {
      duration: 300,
      easings: Object.keys(easings)
    },
    pswpOptions: {
      history: true,
      galleryPIDs: true,
      preload: [1, 3],
      shareEl: false,
      /* eslint-disable-next-line no-unused-vars */
      addCaptionHTMLFn: function (item, captionEl, isFake) {
        if (!item.el.title) {
          captionEl.children[0].innerHTML = ''
          return false
        }
        captionEl.children[0].innerHTML = item.el.title
        return true
      }
    }
  }),
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('app', ['objects', 'error', 'next']),
    ...mapGetters('app', ['objectsByDate']),
    isAdmin () {
      return this.user && this.user.isAdmin
    },
    isAuthorized () {
      return this.user && this.user.isAuthorized
    }
  },
  mounted () {
    window.addEventListener('scroll', this.bottomVisible)
  },
  updated () {
    this.bottom = false
    if (this.$route.hash) {
      this.key = 1 * this.$route.hash.match(/&pid=(.*)/)[1]
    }
  },
  beforeDestroy () {
    window.removeEventListener('scroll', this.bottomVisible)
  },
  watch: {
    bottom: function (val) {
      if (val && this.next) {
        this.$store.dispatch('app/fetchRecords')
      }
    }
  },
  methods: {
    bottomVisible () {
      // https://scotch.io/tutorials/simple-asynchronous-infinite-scroll-with-vue-watchers
      const scrollY = window.scrollY
      const visible = document.documentElement.clientHeight
      const pageHeight = document.documentElement.scrollHeight
      this.bottom = visible + scrollY + this.distance >= pageHeight
    },
    loggedIn (user) {
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
    },
    // download (filename) {
    //   this.$store.dispatch('app/setSnackbar', 'Downloading ' + filename)
    //   // eslint-disable-next-line no-undef
    //   gtag('event', 'download', {
    //     event_category: 'engagement',
    //     event_label: filename,
    //     value: 1
    //   })
    // }
  }
}
</script>
