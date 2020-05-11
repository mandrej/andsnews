<template>
  <div>
    <Edit :visible="editForm" :rec="current" @close="editForm = false"></Edit>

    <Dialog :model="confirm" :persistent="true" title="Want to delete?" :text="current.headline">
      <v-layout justify-space-between row>
        <v-btn color="error" @click="agree">Yes</v-btn>
        <v-btn color="primary" @click="confirm = false">No</v-btn>
      </v-layout>
    </Dialog>

    <v-fab-transition>
      <v-btn
        v-show="count > 0"
        fab
        large
        fixed
        bottom
        right
        style="bottom: 64px; right: 64px"
        @click="$vuetify.goTo(0, options)"
      >
        <v-icon>arrow_upward</v-icon>
      </v-btn>
    </v-fab-transition>

    <v-container fluid grid-list-lg mt-2 class="pa-3">
      <Photoswipe :options="{history: true}">
        <v-layout row wrap v-lazy-container="{ selector: 'img' }">
          <v-flex xs12 sm6 md4 lg3 xl2 v-for="item in objects" :key="item.id">
            <v-card color="white">
              <img
                class="lazy"
                :data-src="getImgSrc(item, 400)"
                :title="caption(item)"
                :data-pswp-size="item.dim.join('x')"
                :data-pswp-src="getImgSrc(item)"
              />
              <v-card-title>{{item.headline}}</v-card-title>
              <v-card-text>
                <v-layout row align-center justify-space-between class="px-2">
                  <span style="line-height: 28px">{{item.date}}</span>
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
                </v-layout>
                <div>by {{item.nick}}</div>
              </v-card-text>
              <v-divider></v-divider>
              <v-card-actions>
                <v-container fluid>
                  <v-layout :class="justify(user)">
                    <v-btn v-if="canDelete(user)" icon small text @click="removeRecord(item)">
                      <v-icon>cancel</v-icon>
                    </v-btn>
                    <v-btn v-if="canEdit(user)" icon small text @click="showEditdForm(item)">
                      <v-icon>edit</v-icon>
                    </v-btn>
                    <v-btn
                      icon
                      small
                      text
                      :href="`/api/download/${item.filename}`"
                      :download="item.filename"
                      @click="download('Downloading ' + item.filename)"
                    >
                      <v-icon>file_download</v-icon>
                    </v-btn>
                  </v-layout>
                </v-container>
              </v-card-actions>
            </v-card>
          </v-flex>

          <v-flex xs12 md8 offset-md-2 py-10 v-if="!objects.length">
            <v-alert
              v-if="error === ''"
              type="info"
              transition="scale-transition"
              prominent
            >No data for current filter/ search</v-alert>
            <v-alert v-else type="error" transition="scale-transition" prominent>
              Something went wrong
              <br />
              {{error}}
            </v-alert>
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
import Photoswipe from 'vue-pswipe'
import common from '@/helpers/mixins'
import * as easings from 'vuetify/lib/services/goto/easing-patterns'

Vue.use(Photoswipe, {
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
})

export default {
  name: 'List',
  components: {
    Edit: () => import(/* webpackChunkName: "edit" */ '@/components/Edit'),
    Dialog: () => import(/* webpackChunkName: "dialog" */ '@/components/Dialog')
  },
  mixins: [common],
  data: () => ({
    isAdmin: false,
    isAuthorized: false,
    bottom: false,
    distance: 2000,
    confirm: false,
    current: {},
    editForm: false,
    options: {
      duration: 300,
      easings: Object.keys(easings)
    }
  }),
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('app', ['objects', 'count', 'error', 'next'])
  },
  mounted () {
    this.isAuthorized = this.user && this.user.isAuthorized
    this.isAdmin = this.user && this.user.isAdmin
    EventBus.$on('signin', user => {
      this.isAuthorized = user && user.isAuthorized
      this.isAdmin = user && user.isAdmin
    })

    window.addEventListener('scroll', this.bottomVisible)
    EventBus.$on('delete', message => {
      EventBus.$emit('snackbar', message)
    })
  },
  updated () {
    this.$nextTick(() => {
      this.bottom = false
    })
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
    },
    justify (user) {
      return (user.isAuthorized) ? 'justify-space-between' : 'justify-end'
    },
    download (msg) {
      EventBus.$emit('snackbar', msg)
      this.$gtag.event('download', {
        event_category: 'engagement',
        event_label: msg,
        non_interaction: true
      })
    }
  }
}
</script>
