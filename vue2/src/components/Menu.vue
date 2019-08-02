<template>
  <v-img :src="getImgSrc(menu[0])" :height="height">
    <v-container>
      <v-layout column fixed align-end class="pa-5">
        <h1 class="display-2 font-weight-light white--text">ANDрејевићи</h1>
        <h4 class="body-1 font-weight-light white--text">{{total}} photos since 2007 and counting …</h4>
      </v-layout>
    </v-container>
    <v-container fill-height>
      <v-layout row align-center justify-center>
        <v-btn fab dark large outlined
          class="big"
          @click="showFilter(menu[0])">
          <v-icon>arrow_downward</v-icon>
        </v-btn>
      </v-layout>
    </v-container>
  </v-img>
</template>

<script>
import { mapState } from 'vuex'
import common from '@/helpers/mixins'
import { EventBus } from '@/helpers/event-bus'

export default {
  name: 'Menu',
  mixins: [ common ],
  data: () => ({
    height: null
  }),
  computed: {
    ...mapState('app', ['menu', 'total', 'values'])
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
