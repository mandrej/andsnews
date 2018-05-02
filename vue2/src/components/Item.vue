<template>
  <div>
    <v-dialog v-model="info" hide-overlay lazy max-width="360px">
      <v-card>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn icon flat @click.native="info = false">
             <v-icon>close</v-icon>
          </v-btn>
        </v-card-actions>
        <v-card-text>
          <p class="title">{{dateFormat(rec.date)}}</p>
          <p>
            {{rec.author}}<br>
            {{rec.model}} {{rec.lens}} ({{rec.focal_length}}mm)
          </p>
          <p class="title">f{{rec.aperture}} {{rec.shutter}}s {{rec.iso}} ASA</p>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog
      v-model="show"
      lazy
      fullscreen
      transition="scale-transition"
      hide-overlay
      scrollable>
      <v-card tile>
        <v-toolbar card light>
          <v-btn icon @click.native="show = false">
            <v-icon>close</v-icon>
          </v-btn>
          <v-toolbar-title>{{rec.headline || title}}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon :href="`/api/download/${rec.safekey}`" flat>
            <v-icon>file_download</v-icon>
          </v-btn>
          <v-btn icon @click="info = true" flat>
            <v-icon>more_vert</v-icon>
          </v-btn>
        </v-toolbar>
        <v-card-media>
          <v-carousel :value="index" :cycle="false"
            @input="currentIndex" hide-delimiters lazy>
            <v-carousel-item v-for="item in objects" :key="item.safekey"
              v-lazy:background-image="getImgSrc(item)"
              style="background-size: contain; background-position: 50% 50%">
            </v-carousel-item>
          </v-carousel>
        </v-card-media>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import common from '../../helpers/mixins'

export default {
  name: 'Item',
  mixins: [ common ],
  props: ['visible', 'index'],
  data: () => ({
    rec: {},
    title: 'Not found',
    info: false
  }),
  computed: {
    ...mapState(['user', 'objects', 'pages', 'next', 'filter', 'busy'])
  },
  methods: {
    currentIndex (idx) {
      this.rec = this.objects[idx]
      if ((this.objects.length - idx) === 3) this.loadMore()
    },
    loadMore () {
      if (this.objects.length === 0) {
        this.$store.dispatch('fetchRecords')
      } else if (this.next && this.pages.indexOf(this.next) === -1) {
        this.$store.dispatch('fetchRecords', this.next)
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.carousel {
  height: calc(100vh - 56px);
}
</style>
