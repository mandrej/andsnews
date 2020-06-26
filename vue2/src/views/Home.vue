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
      <h4 class="body-1 white--text text-right">
        ANDрејевићи personal photo album
        <br />
        {{total}} photos since 2007 and counting
        <br />
        occupying {{formatBytes(bucket + bytes)}} of cloud space
      </h4>
    </div>
    <v-avatar absolute size="70%" @click="$router.push({name: 'list', query: query})">
      <img src="/static/aperture.svg" />
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
    ...mapState('app', ['last', 'total', 'bytes']),
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
