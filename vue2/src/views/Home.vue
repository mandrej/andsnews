<template>
  <div
    v-lazy:background-image="getImgSrc(last)"
    class="d-flex flex-column fill-height align-center justify-center lazy last"
    @click="$router.push({name: 'list', query: query})"
    style="cursor: pointer"
  >
    <div class="pa-5" style="position: absolute; top: 0; right: 0">
      <h4 class="text-body-1 white--text text-right">
        ANDрејевићи personal photo album
        <br />
        {{count}} photos since 2007 and counting
      </h4>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'

export default {
  name: 'Home',
  mixins: [common],
  mounted () {
    this.$store.dispatch('app/bucketInfo', { verb: 'get' })
  },
  computed: {
    ...mapState('app', ['last', 'bucket']),
    count () { return this.bucket.count },
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
