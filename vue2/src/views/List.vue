<template>
  <div>
    <Edit :visible="editForm" :current="current" @close="closEdit"></Edit>

    <v-dialog v-model="confirm" max-width="300px" persistent>
      <v-card>
        <v-card-title class="text-h5" primary-title>{{current.headline}}</v-card-title>
        <v-card-text>Want to delete?</v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="flex-row justify-space-between px-6 py-4">
          <v-btn color="primary" @click="agree">Yes</v-btn>
          <v-btn color="error" @click="closeConfirm">No</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- vuetify/packages/docs/src/layouts/default/FabToTop.vue -->
    <v-fab-transition>
      <v-btn
        v-show="fab"
        fab
        icon
        large
        fixed
        bottom
        right
        class="secondary elevation-2"
        style="bottom: 32px; right: 32px"
        v-scroll="onScroll"
        @click="$vuetify.goTo(0)"
      >
        <v-icon>arrow_upward</v-icon>
      </v-btn>
    </v-fab-transition>

    <v-container fluid class="pa-4 py-5">
      <Photoswipe v-if="error === null" :options="options" :key="pid">
        <v-row v-lazy-container="{ selector: 'img' }" class="mx-n2">
          <v-col
            cols="12"
            sm="6"
            md="4"
            lg="3"
            xl="2"
            v-for="item in objects"
            :key="item.id"
            class="pa-2"
          >
            <v-card :id="'card_' + item.id" flat>
              <v-responsive :aspect-ratio="4/3">
                <img
                  class="lazy"
                  :data-src="getImgSrc(item, 400)"
                  :title="caption(item)"
                  :data-pswp-size="item.dim.join('x')"
                  :data-pswp-src="getImgSrc(item)"
                  :data-pswp-pid="item.id"
                />
                <p class="text-h6 text-truncate" style="width: 100%">{{item.headline}}</p>
              </v-responsive>
              <v-card-text class="d-flex justify-space-between py-2">
                <div
                  style="line-height: 28px"
                >{{item.nick}}, {{$date(item.date).format('ddd DD.MM.YYYY HH:mm')}}</div>
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
              <template v-if="user.isAuthorized">
                <v-divider></v-divider>
                <v-card-actions class="justify-space-between">
                  <v-btn v-if="user.isAdmin" icon small text @click.stop="removeRecord(item)">
                    <v-icon>delete</v-icon>
                  </v-btn>
                  <v-btn icon small text @click.stop="showEditdForm(item)">
                    <v-icon>edit</v-icon>
                  </v-btn>
                  <v-btn
                    icon
                    small
                    text
                    @click="register(item)"
                    :href="`/api/download/${item.filename}`"
                    :download="item.filename"
                  >
                    <v-icon>file_download</v-icon>
                  </v-btn>
                </v-card-actions>
              </template>
            </v-card>
          </v-col>
        </v-row>
      </Photoswipe>
      <v-alert
        v-else-if="error === 0"
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
import { mapState } from 'vuex'
import Photoswipe from 'vue-pswipe'
import common from '@/helpers/mixins'

Vue.use(Photoswipe)

export default {
  name: 'List',
  mixins: [common],
  components: {
    Edit: () => import(/* webpackChunkName: "edit" */ '@/components/Edit')
  },
  data: () => ({
    pid: null,
    bottom: false,
    fab: false,
    current: {},
    confirm: false,
    editForm: false,
    options: {
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
  mounted () {
    const self = this
    window.onpopstate = function () {
      if (self.editForm) self.editForm = false
      if (self.confirm) self.confirm = false
    }
  },
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('app', ['objects', 'error', 'next'])
  },
  updated () {
    this.bottom = false
    if (this.$route.hash) {
      const pid = +this.$route.hash.match(/&pid=(.*)/)[1]
      this.$nextTick(() => {
        if (pid !== this.pid) this.$vuetify.goTo('#card_' + pid)
        this.pid = pid
      })
    }
  },
  watch: {
    bottom: function (val) {
      if (val && this.next) {
        this.$store.dispatch('app/fetchRecords')
      }
    }
  },
  methods: {
    onScroll () {
      const clientHeight = document.documentElement.clientHeight
      const scrollHeight = document.documentElement.scrollHeight
      const topOffset = (
        window.pageYOffset ||
        document.documentElement.offsetTop ||
        0
      )
      this.fab = topOffset > 300
      this.bottom = topOffset + clientHeight + 2000 >= scrollHeight
    },
    showEditdForm (item) {
      this.current = { ...item }
      window.history.pushState({}, '') // fake history
      this.editForm = true
    },
    removeRecord (item) {
      this.current = { ...item }
      window.history.pushState({}, '')
      this.confirm = true
    },
    closEdit () {
      window.history.back() // consume fake history
      this.editForm = false
    },
    closeConfirm () {
      window.history.back()
      this.confirm = false
    },
    agree () {
      this.$store.dispatch('app/deleteRecord', this.current)
      window.history.back()
      this.confirm = false
    },
    register (item) {
      // eslint-disable-next-line no-undef
      gtag('event', 'download', {
        event_category: 'engagement',
        event_label: item.headline + ' (' + this.user.email + ')',
        value: 1
      })
    },
    caption (item) {
      const { headline, aperture, shutter, iso, model, lens } = item
      let tmp = headline
      tmp += (aperture) ? ' f' + aperture : ''
      tmp += (shutter) ? ', ' + shutter + 's' : ''
      tmp += (iso) ? ', ' + iso + ' ASA' : ''
      tmp += (model) ? '<br>' + model : ''
      tmp += (lens) ? ', ' + lens : ''
      return tmp
    }
  }
}
</script>
