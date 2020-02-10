<template>
  <Layout>
    <template v-slot:drawer>
      <v-navigation-drawer v-model="drawer" app fixed clipped :width="300">
        <v-layout column fill-height>
          <Find></Find>
          <v-spacer></v-spacer>
          <Menu></Menu>
        </v-layout>
      </v-navigation-drawer>
    </template>

    <template v-slot:appbar>
      <div class="hamburger">
        <v-app-bar-nav-icon dark class="hidden-lg-and-up pa-2" @click="drawer = !drawer"></v-app-bar-nav-icon>
      </div>
    </template>

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
import Menu from '@/components/Menu'
import Find from '@/components/Find'
import common from '@/helpers/mixins'

export default {
  name: 'Home',
  components: {
    Layout,
    Find,
    Menu
  },
  mixins: [common],
  data: () => ({
    drawer: null
  }),
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
