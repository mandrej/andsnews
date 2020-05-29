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
  maxAge: 1000 * 60 * 60, // 1 hour
})

const opts = {
  theme: {
    dark: false,
    themes: {
      light: {
        primary: colors.indigo.darken2,
        secondary: colors.lime.darken1,
        accent: colors.orange.lighten2
      },
      dark: {
        primary: colors.teal,
        secondary: colors.lime.darken1,
        accent: colors.brown
      }
    },
    options: {
      customProperties: true,
      themeCache
    }
  },
  icons: {
    iconfont: 'md'
  }
}

export default new Vuetify(opts)
