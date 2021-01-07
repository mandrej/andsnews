<template>
  <div>
    <Edit :visible="editForm" @close="editForm = false"></Edit>

    <v-dialog v-model="confirm" max-width="300px" persistent>
      <v-card color="secondary">
        <v-card-title class="headline" primary-title>{{current.headline}}</v-card-title>
        <v-card-text>Want to delete?</v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="flex-row justify-space-between px-6 py-4">
          <v-btn color="error" @click="agree">Yes</v-btn>
          <v-btn color="success" @click="confirm = false">No</v-btn>
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
        :class="$vuetify.theme.dark ? 'accent elevation-2 white--text' : 'accent elevation-2 black--text'"
        style="bottom: 32px; right: 32px"
        v-scroll="onScroll"
        @click="$vuetify.goTo(0)"
      >
        <v-icon>arrow_upward</v-icon>
      </v-btn>
    </v-fab-transition>

    <Photoswipe :options="options" :key="pid">
      <v-container fluid class="pa-4">
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
            <Card :id="'card_' + item.id" :item="item"></Card>
          </v-col>
        </v-row>
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
import { mapState } from 'vuex'
import Photoswipe from 'vue-pswipe'
import common from '@/helpers/mixins'

Vue.use(Photoswipe)

export default {
  name: 'List',
  mixins: [common],
  components: {
    Card: () => import(/* webpackChunkName: "card" */ '@/components/Card'),
    Edit: () => import(/* webpackChunkName: "edit" */ '@/components/Edit')
  },
  data: () => ({
    pid: null,
    bottom: false,
    fab: false,
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
    ...mapState('app', ['objects', 'error', 'next', 'current'])
  },
  mounted () {
    this.$eventBus.on('show-edit', () => { this.editForm = true })
    this.$eventBus.on('show-confirm', () => { this.confirm = true })
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
    agree () {
      this.$store.dispatch('app/deleteRecord', this.current)
      this.confirm = false
    }
  }
}
</script>
