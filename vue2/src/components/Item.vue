<template>
  <div>
    <!-- <v-dialog v-model="info" hide-overlay lazy max-width="360px">
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
    </v-dialog> -->

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
        <v-card-text>
          <swiper ref="mySwiper" :options="swiperOption"
            @slideChange="slideChange"
            @reachEnd="loadMore">
            <swiper-slide v-for="item in objects" :key="item.safekey"
              :data-background="getImgSrc(item)" class="swiper-slide swiper-lazy">
            </swiper-slide>
            <div class="swiper-button-prev swiper-button-white" slot="button-prev"></div>
            <div class="swiper-button-next swiper-button-white" slot="button-next"></div>
          </swiper>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import 'swiper/dist/css/swiper.css'
import { swiper, swiperSlide } from 'vue-awesome-swiper'
import common from '../../helpers/mixins'

export default {
  name: 'Item',
  components: {
    swiper,
    swiperSlide
  },
  mixins: [ common ],
  props: ['visible', 'index'],
  data: () => ({
    idx: 0,
    rec: {},
    title: 'Not found',
    swiperOption: {
      lazy: true,
      initialSlide: 3,
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev'
      }
    },
    info: false
  }),
  computed: {
    ...mapState(['user', 'objects', 'pages', 'next', 'filter', 'busy']),
    mySwiper () {
      return this.$refs.mySwiper.swiper
    }
  },
  watch: {
    index (newVal, oldVal) {
      if (oldVal) {
        this.idx = oldVal
      }
    },
    idx (newVal, oldVal) {
      if (newVal) {
        this.rec = this.objects[newVal]
        // this.mySwiper.slideTo(newVal)
      }
    }
  },
  methods: {
    slideChange () {
      this.idx = this.mySwiper.activeIndex
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
.card__text {
  padding: 0;
}
.swiper-slide {
  width: 100%;
  height: calc(100vh - 56px);
  background-position: center;
  background-size: contain;
}
</style>
