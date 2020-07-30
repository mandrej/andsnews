import Vue from 'vue'
import Vuetify, { VList } from 'vuetify/lib'
import colors from 'vuetify/lib/util/colors'
import LRU from 'lru-cache'

Vue.use(Vuetify, {
  components: {
    VList
  }
})
const themeCache = new LRU({
  max: 10,
  maxAge: 24 * 60 * 60 * 1000, // 1 day
})

const opts = {
  theme: {
    dark: false,
    themes: {
      light: {
        primary: colors.blueGrey,
        secondary: colors.blueGrey.lighten3,
        accent: colors.orange.lighten2,
        error: colors.deepOrange
      },
      dark: {
        primary: colors.teal,
        secondary: colors.teal.darken3,
        accent: colors.brown,
        error: colors.deepOrange
      }
    },
    options: {
      themeCache
    }
  },
  icons: {
    iconfont: 'md'
  }
}

export default new Vuetify(opts)
