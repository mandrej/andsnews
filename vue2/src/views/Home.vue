<template>
  <Layout :find="find">
    <v-layout
      column
      fill-height
      align-center
      justify-center
      v-lazy:background-image="getImgSrc(last)"
      class="last"
    >
      <div class="pa-5" style="position: absolute; top: 0; right: 0">
        <h1 class="display-2 font-weight-light white--text">ANDрејевићи</h1>
        <h4 class="body-1 white--text">{{total}} photos since 2007 and counting …</h4>
      </div>
      <v-avatar absolute size="70%" @click="showFilter(last)">
        <img src="/static/img/aperture.svg" />
      </v-avatar>
    </v-layout>
  </Layout>
</template>

<script>
import { mapState } from 'vuex'
import Layout from '@/components/Layout'
import common from '@/helpers/mixins'

export default {
  name: 'Home',
  components: {
    Layout
  },
  props: ['find'],
  mixins: [common],
  computed: {
    ...mapState('app', ['last', 'total'])
  },
  methods: {
    showFilter (rec) {
      this.$router.push({
        name: 'list',
        query: {
          year: rec.value
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.hamburger {
  position: absolute;
  top: 0;
  left: 0;
  padding: 6px;
  z-index: 2;
}
.last {
  background-size: cover;
  background-position: center;
}
</style>
