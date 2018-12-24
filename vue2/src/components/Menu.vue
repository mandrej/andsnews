<template>
  <v-container fluid grid-list-lg>
    <v-parallax :src="getImgSrc(menu[0])" height="440" light>
      <v-layout align-center column justify-center>
        <h1 class="display-2 font-weight-light mb-3">ANDрејевићи</h1>
        <h4 class="subheading text-xs-center">our photo album since 2007</h4>
      </v-layout>
    </v-parallax>

    <div style="position: relative">
      <h1 class="headline font-weight-light text-xs-center mt-2">Filters</h1>
      <v-btn v-if="canAdd(user)"
        fab medium absolute bottom right
        style="bottom: 12px; z-index: 1"
        color="accent" class="black--text" @click="$router.push({ name: 'add' })">
        <v-icon>add</v-icon>
      </v-btn>
    </div>
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
          <v-card-title @click="showFilter(item)" style="cursor: pointer">
            <div>
              <h3 class="title">{{justName(item)}}</h3>
              <div>{{item.count}} photos</div>
            </div>
          </v-card-title>
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
    ...mapState('auth', ['user']),
    ...mapState('app', ['menu'])
  },
  methods: {
    canAdd (user) {
      return user.isAuthorized
    },
    showFilter (rec) {
      const sep = '"'
      const value = (rec.field_name === 'email')
        ? rec.field_name + ':' + sep + this.getName(rec.name) + sep
        : rec.field_name + ':' + sep + rec.name + sep
      this.$router.push({ name: 'list', params: { 'qs': value } })
    },
    justName (rec) {
      return (rec.field_name === 'email') ? this.getName(rec.name) : rec.name
    }
  }
}
</script>
