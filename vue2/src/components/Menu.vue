<template>
  <v-container fluid grid-list-lg>
    <v-layout row wrap>
      <v-flex xs12 sm6 md4 lg3 xl2
        v-for="(item, i) in menu" :key="i">
        <v-card light>
          <v-img
            cover
            height="200px"
            aspect-ratio="1.0"
            class="white--text"
            style="cursor: pointer"
            @click="showFilter(item)"
            :src="getImgSrc(item, 's')">
            <v-container fill-height fluid>
              <v-layout fill-height>
                <v-flex xs12 align-end flexbox>
                  <span class="headline">{{item.name}}</span>
                </v-flex>
              </v-layout>
            </v-container>
          </v-img>
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
import common from '@/helpers/mixins'

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
