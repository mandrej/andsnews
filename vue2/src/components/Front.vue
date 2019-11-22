<template>
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
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'
import { EventBus } from '@/helpers/event-bus'

export default {
  name: 'Front',
  mixins: [common],
  data: () => ({
    height: null
  }),
  created () {
    this.$store.dispatch('app/_fetchLast')
    this.$store.dispatch('app/fetchTotal')
  },
  computed: {
    ...mapState('app', ['last', 'total'])
  },
  mounted () {
    this.height = document.documentElement.clientHeight
    EventBus.$on('resize', () => {
      this.height = document.documentElement.clientHeight
    })
  },
  methods: {
    showFilter (rec) {
      const tmp = {}
      tmp[rec.field_name] = rec.name
      this.$router.push({ name: 'list', query: tmp })
    }
  }
}
</script>

<style lang="scss" scoped>
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
