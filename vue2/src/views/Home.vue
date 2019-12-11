<template>
  <Layout v-resize="onResize">
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
      <div class="front">
        <v-app-bar-nav-icon dark class="hidden-lg-and-up pa-2" @click="drawer = !drawer"></v-app-bar-nav-icon>
      </div>
    </template>

    <v-img :src="getImgSrc(last)" :height="height">
      <div class="pa-5" style="position: absolute; top: 0; right: 0">
        <h1 class="display-2 font-weight-light white--text">ANDрејевићи</h1>
        <h4 class="body-1 white--text">{{total}} photos since 2007 and counting …</h4>
      </div>
      <v-layout column fill-height align-center justify-center>
        <v-btn fab dark large outlined class="big" @click="showFilter(last)">
          <v-icon>arrow_downward</v-icon>
        </v-btn>
      </v-layout>
    </v-img>
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
    drawer: null,
    height: null
  }),
  created () {
    this.$store.dispatch('app/_fetchLast')
    this.$store.dispatch('app/fetchTotal')
  },
  mounted () {
    this.height = document.documentElement.clientHeight
    this.$on('resize', () => {
      this.height = document.documentElement.clientHeight
    })
  },
  computed: {
    ...mapState('app', ['last', 'total'])
  },
  methods: {
    showFilter (rec) {
      const tmp = {}
      tmp[rec.field_name] = rec.name
      this.$router.push({ name: 'list', query: tmp })
    },
    onResize () {
      this.$emit('resize')
    }
  }
}
</script>

<style lang="scss" scoped>
.front {
  position: absolute;
  top: 0;
  left: 0;
  padding: 6px;
  z-index: 2;
}
.big {
  height: 150px;
  width: 150px;
  border: 2px solid currentColor;
  .v-icon {
    height: 65px;
    font-size: 65px;
    width: 65px;
  }
}
</style>
