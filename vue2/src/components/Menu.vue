<template>
  <v-container fluid grid-list-lg>
    <h4 class="title font-weight-regular text-right">{{total}} photos in our album since 2007</h4>
    <v-layout row wrap>
      <v-flex xs12 sm6 md4 lg3 xl2
        v-for="item in menu" :key="item.name">
        <v-card light>
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
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Menu',
  mixins: [ common ],
  computed: {
    ...mapState('app', ['menu', 'total', 'values'])
  },
  methods: {
    showFilter (rec) {
      const tmp = {}
      switch (rec.field_name) {
        case 'tags':
          tmp[rec.field_name] = [rec.name]
          break
        case 'email':
          tmp['nick'] = this.email2nick(rec.name)
          break
        default:
          tmp[rec.field_name] = rec.name
      }
      this.$store.dispatch('app/saveFindForm', tmp)
      this.$router.push({ name: 'list', query: tmp })
    },
    justName (rec) {
      return (rec.field_name === 'email') ? 'by ' + this.email2nick(rec.name) : rec.name
    }
  }
}
</script>
