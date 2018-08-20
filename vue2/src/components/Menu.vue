<template>
  <v-container fluid grid-list-lg>
    <v-layout row wrap>
      <v-flex xs12 sm6 md4 lg3 xl2
        v-for="(item, i) in menu" :key="i">
        <v-card light>
          <v-card-media
            @click="showFilter(item)"
            class="white--text"
            height="150px"
            v-lazy:background-image="getImgSrc(item, 's')">
            <v-container fill-height fluid>
              <v-layout fill-height>
                <v-flex xs12 align-end flexbox>
                  <span class="headline">{{item.name}}</span>
                </v-flex>
              </v-layout>
            </v-container>
          </v-card-media>
          <v-card-text>
            {{item.count}} photos
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import VueLazyload from 'vue-lazyload'
import common from '@/helpers/mixins'

Vue.use(VueLazyload, {
  attempt: 1
})

export default {
  name: 'Menu',
  mixins: [ common ],
  mounted () {
    this.$store.dispatch('All/fetchMenu')
  },
  computed: {
    ...mapState('All', ['menu'])
  },
  methods: {
    showFilter (rec) {
      const sep = '"'
      const value = rec.field_name + ':' + sep + rec.name + sep
      this.$router.push({ name: 'list', params: { 'qs': value }})
    }
  }
}
</script>

<style lang="scss" scoped>
.v-card__media {
  opacity: 0;
  background-position: center;
  transition: all 0.3s ease-in;
  &[lazy=loaded] {
    opacity: 1;
  }
}
</style>
