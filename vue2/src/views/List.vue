<template>
  <div>
    <Edit :visible="editForm" :current="current" @close="closEdit"></Edit>

    <v-dialog v-model="confirm" max-width="300px" persistent>
      <v-card>
        <v-card-title class="text-h5" primary-title>{{
          current.headline
        }}</v-card-title>
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

    <Photoswipe v-if="error === null" :options="options" :key="refreshKey">
      <v-container
        fluid
        v-for="(list, date) in objectsByDate"
        :key="date"
        class="pa-4"
      >
        <h2 class="pb-2 font-weight-light">
          {{ $date(date).format('dddd, MMMM DD, YYYY') }}
        </h2>
        <v-row class="mx-n2">
          <template v-for="item in list">
            <v-col
              :key="item.id"
              cols="12"
              sm="6"
              md="4"
              lg="3"
              xl="2"
              class="pa-2"
            >
              <v-lazy :options="{ threshold: 0.5 }" min-height="200" transition="fade-transition">
                <Card
                  :id="'card_' + item.id"
                  :item="item"
                  @remove-record="removeRecord"
                  @edit-record="showEditdForm"
                  @register-download="registerDownload"
                ></Card>
              </v-lazy>
            </v-col>
          </template>
        </v-row>
      </v-container>
    </Photoswipe>

    <v-container v-else-if="error === 0" fluid class="pa-4">
      <v-alert type="info" transition="scale-transition" prominent
        >No data for current filter/ search</v-alert
      >
    </v-container>
    <v-container v-else fluid class="pa-4">
      <v-alert type="error" transition="scale-transition" prominent>
        Something went wrong
        <br />
        {{ error }}
      </v-alert>
    </v-container>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState, mapGetters } from 'vuex'
import Card from '../components/Card'
import Photoswipe from 'vue-pswipe'

Vue.use(Photoswipe)

export default {
  name: 'List',
  components: {
    Card,
    Edit: () => import(/* webpackChunkName: "edit" */ '../components/Edit')
  },
  data: () => ({
    refreshKey: null,
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
  computed: {
    ...mapState('app', ['error', 'next']),
    ...mapGetters('app', ['objectsByDate'])
  },
  mounted () {
    const self = this
    window.onpopstate = function () {
      if (self.editForm) self.editForm = false
      if (self.confirm) self.confirm = false
    }
  },
  updated () {
    if (!this.$route.hash) return
    const pid = +this.$route.hash.match(/&pid=(.+)/)[1] || null
    if (pid !== this.refreshKey) {
      this.$nextTick(() => {
        this.$vuetify.goTo('#card_' + pid)
        this.refreshKey = pid
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
      const topOffset = window.pageYOffset || 0
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

      this.$anime
        .timeline({
          targets: '#card_' + this.current.id,
          duration: 200,
          easing: 'easeInOutQuart'
        })
        .add({ scale: 1.05 })
        .add({ scale: 1 })
    },
    closeConfirm () {
      window.history.back()
      this.confirm = false
    },
    agree () {
      this.$store.dispatch('app/deleteRecord', this.current)
      window.history.back()
      this.confirm = false

      this.$anime({
        targets: '#card_' + this.current.id,
        opacity: 0,
        easing: 'easeOutQuart',
        delay: 1000,
        duration: 2000
      })
    },
    registerDownload (data) {
      // eslint-disable-next-line no-undef
      gtag('event', 'download', {
        event_category: 'engagement',
        event_label: data.headline + ' (' + data.email + ')',
        value: 1
      })
    }
  }
}
</script>
