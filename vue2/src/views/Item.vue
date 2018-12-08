<template>
  <div>
    <Info :visible="showInfo" :item="item" @close="showInfo = false"></Info>

    <v-app>
      <v-toolbar app light class="aperture">
        <v-btn icon @click="$router.push({ name: 'home' })">
          <v-icon>home</v-icon>
        </v-btn>
        <v-toolbar-title class="headline">{{item.headline}}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon @click="showInfo = true" flat>
          <v-icon>more_vert</v-icon>
        </v-btn>
      </v-toolbar>

      <v-content>
        <v-container fluid>
          <v-img :src="getImgSrc(item)" contain></v-img>
        </v-container>
      </v-content>

      <Footer/>
    </v-app>
  </div>
</template>

<script>
import Vue from 'vue'
import common from '@/helpers/mixins'

const axios = Vue.axios

export default {
  name: 'Item',
  components: {
    'Info': () => import(/* webpackChunkName: "info" */ '@/components/Info'),
    'Footer': () => import(/* webpackChunkName: "footer" */ '@/components/Footer')
  },
  props: ['safekey'],
  mixins: [ common ],
  data: () => ({
    showInfo: false,
    item: {}
  }),
  mounted () {
    axios.get(this.safekey)
      .then(response => {
        this.item = response.data
      })
  }
}
</script>
