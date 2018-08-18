<template>
  <div>
    <v-container fluid grid-list-lg>
      <v-layout row wrap>
        <v-flex xs12 sm6 md4 lg3 xl2
          v-for="(item, i) in menu" :key="i">
          <div class="square">
            <img :alt="alt(item)"
              v-lazy="getImgSrc(item, 's')"
              @click="showFilter(item)">
            <v-list>
              <v-list-tile>
                <v-list-tile-content>
                  <v-list-tile-title>{{item.name}}</v-list-tile-title>
                </v-list-tile-content>
                <v-list-tile-action>
                  <v-list-tile-sub-title>{{item.count}}</v-list-tile-sub-title>
                </v-list-tile-action>
              </v-list-tile>
            </v-list>
          </div>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import VueLazyload from 'vue-lazyload'
import common from '@/helpers/mixins'

Vue.use(VueLazyload, {
  attempt: 1
})

export default {
  name: 'Menu',
  mixins: [ common ],
  data: () => ({

  }),
  mounted () {
    this.$store.dispatch('All/fetchMenu')
  },
  computed: {
    ...mapState('All', ['user', 'menu', 'busy'])
  },
  methods: {
    showFilter (rec) {
      const sep = '"'
      this.$store.dispatch('All/changeFilter', {
        field: 'search',
        value: rec.field_name + ':' + sep + rec.name + sep
      })
    },
    alt (rec) {
      return `${rec.field_name + '/' + rec.name}`
    }
  }
}
</script>

<style lang="scss" scoped>
.square {
  img {
    display: inherit;
    max-width: 100%;
    opacity: 0;
    transition: all 0.5s ease-in;
    &[lazy=loaded] {
      opacity: 1;
    }
  }
}
.v-list__tile__title, .v-list__tile__sub-title {
  font-size: 20px;
}
.v-list__tile__sub-title {
  text-align: right;
}
</style>
