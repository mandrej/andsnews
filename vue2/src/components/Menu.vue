<template>
  <div>
    <v-parallax v-if="height" :src="getImgSrc(menu[0])" :height="height">
      <v-layout dark align-center column justify-center
        @click="showFilter(menu[0])"
        style="cursor: pointer">
        <h1 class="display-2 font-weight-light">ANDрејевићи</h1>
        <h4 class="subheading mb-3">{{total}} photos in our album since 2007</h4>
      </v-layout>
    </v-parallax>

    <v-container fluid grid-list-lg>
      <v-layout row wrap>
        <v-flex xs12 sm6 md4 lg3 xl2
          v-for="item in menu" :key="item.name">
          <v-card text light>
            <v-img
              cover
              height="150px"
              aspect-ratio="1"
              style="cursor: pointer"
              @click="showFilter(item)"
              :src="getImgSrc(item, '400-c')">
            </v-img>
            <v-card-title style="cursor: pointer" @click="showFilter(item)">
                {{justName(item)}}
            </v-card-title>
            <v-card-text>{{item.count}} photos</v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'
import { EventBus } from '@/helpers/event-bus'

export default {
  name: 'Menu',
  mixins: [ common ],
  data: () => ({
    height: null
  }),
  computed: {
    ...mapState('app', ['menu', 'total'])
  },
  mounted () {
    this.height = document.documentElement.clientHeight - 104
    EventBus.$on('resize', () => {
      this.height = document.documentElement.clientHeight - 104
    })
  },
  methods: {
    showFilter (rec) {
      const tmp = {}
      switch (rec.field_name) {
        case 'tags':
          tmp[rec.field_name] = [rec.name]
          break
        default:
          tmp[rec.field_name] = rec.name
      }
      this.$store.dispatch('app/saveFindForm', tmp)
      this.$router.push({ name: 'list', query: tmp })
    },
    justName (rec) {
      return (rec.field_name === 'nick') ? 'by ' + rec.name : rec.name
    }
  }
}
</script>
