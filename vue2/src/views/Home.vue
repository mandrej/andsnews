<template>
  <v-layout
    column
    fill-height
    align-center
    justify-center
    v-lazy:background-image="getImgSrc(last)"
    class="last"
  >
    <div class="pa-5" style="position: absolute; top: 0; right: 0">
      <h4 class="body-1 white--text">
        ANDрејевићи personal photo album.
        <br />
        {{total}} photos since 2007 and counting
      </h4>
    </div>
    <v-avatar absolute size="70%" @click="$router.push({name: 'list', query: query})">
      <img v-show="!$vuetify.theme.dark" src="/static/aperture-light.svg" />
      <img v-show="$vuetify.theme.dark" src="/static/aperture-dark.svg" />
    </v-avatar>
  </v-layout>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Home',
  mixins: [common],
  computed: {
    ...mapState('app', ['last', 'total']),
    query () {
      return {
        year: this.last.value
      }
    }
  }
}
</script>

<style scoped>
.last {
  background-size: cover;
  background-position: center;
}
</style>
