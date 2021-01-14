import Vue from 'vue'
import Vuetify, { VList } from 'vuetify/lib'
import colors from 'vuetify/lib/util/colors'

Vue.use(Vuetify, {
  components: {
    VList
  }
})

const opts = {
  theme: {
    dark: false,
    themes: {
      light: {
        primary: colors.teal,
        secondary: colors.teal.lighten3,
        accent: colors.teal.accent3,
      },
      dark: {
        primary: colors.teal.darken1,
        secondary: colors.teal.darken3,
        accent: colors.teal.darken2,
      }
    },
    options: {
      customProperties: true
    },
  },
  icons: {
    iconfont: 'md'
  }
}

export default new Vuetify(opts)
