<template>
  <v-container fluid grid-list-lg>
    <v-parallax :src="getImgSrc(menu[0])" light>
      <v-layout align-center column justify-center>
        <h1 class="display-2 font-weight-thin mb-3">ANDрејевићи</h1>
        <h4 class="subheading text-xs-center">our photo album</h4>
      </v-layout>
    </v-parallax>

    <h1 class="headline font-weight-thin text-xs-center mt-2">Filters</h1>
    <v-layout row wrap>
      <v-flex xs12 sm6 md4 lg3 xl2
        v-for="item in menu" :key="item.name">
        <v-card light>
          <v-img
            cover
            height="150px"
            aspect-ratio="1"
            class="white--text"
            style="cursor: pointer"
            @click="showFilter(item)"
            :src="getImgSrc(item, '400-c')">
            <v-container fill-height fluid>
              <v-layout fill-height>
                <v-flex xs12 align-end flexbox>
                  <div class="headline">{{item.name}}</div>
                  <div>{{item.count}} photos</div>
                </v-flex>
              </v-layout>
            </v-container>
          </v-img>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Menu',
  mixins: [ common ],
  computed: {
    ...mapState('app', ['menu'])
  },
  methods: {
    showFilter (rec) {
      const sep = '"'
      const value = rec.field_name + ':' + sep + rec.name + sep
      this.$router.push({ name: 'list', params: { 'qs': value } })
    }
  }
}
</script>
