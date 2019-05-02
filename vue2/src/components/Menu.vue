<template>
  <div>
    <v-parallax v-if="height" :src="getImgSrc(menu[0])" :height="height">
      <v-layout dark align-center column justify-center
        @click="showFilter(menu[0])"
        style="cursor: pointer">
        <h1 class="display-2 font-weight-light">ANDрејевићи</h1>
        <h4 class="subheading mb-3">{{total}} photos in our album since 2007</h4>
      </v-layout>
    </v-parallax>

    <div style="position: relative">
      <h1 class="headline font-weight-light text-xs-center mt-3">Collections</h1>
      <v-btn v-if="canAdd(user)"
        fab medium absolute bottom right
        style="bottom: 20px"
        color="accent" class="black--text" @click="$router.push({ name: 'add' })">
        <v-icon>add</v-icon>
      </v-btn>
    </div>

    <v-container fluid grid-list-lg class="pa-3">
      <v-layout row wrap>
        <v-flex xs12 sm6 md4 lg3 xl2
          v-for="item in menu" :key="item.name">
          <v-card flat light>
            <v-img
              cover
              height="150px"
              aspect-ratio="1"
              style="cursor: pointer"
              @click="showFilter(item)"
              :src="getImgSrc(item, '400-c')">
            </v-img>
            <v-card-title @click="showFilter(item)" style="cursor: pointer">
              <div>
                <h3 class="title">{{justName(item)}}</h3>
                <div>{{item.count}} photos</div>
              </div>
            </v-card-title>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
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
    ...mapState('auth', ['user']),
    ...mapState('app', ['menu', 'total'])
  },
  mounted () {
    this.height = document.documentElement.clientHeight - 104
    EventBus.$on('resize', () => {
      this.height = document.documentElement.clientHeight - 104
    })
  },
  methods: {
    canAdd (user) {
      return user.isAuthorized
    },
    showFilter (rec) {
      const tmp = {}
      switch (rec.field_name) {
        case 'tags':
          tmp[rec.field_name] = [rec.name]
          break
        default:
          tmp[rec.field_name] = rec.name
      }
      this.$store.dispatch('app/saveFindForm', tmp)
      this.$router.push({ name: 'list', query: tmp })
    },
    justName (rec) {
      return (rec.field_name === 'nick') ? 'by ' + rec.name : rec.name
    }
  }
}
</script>
