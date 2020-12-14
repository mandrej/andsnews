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
        background: colors.grey.lighten3,
        primary: colors.grey.darken3,
        secondary: colors.shades.white,
        accent: colors.indigo.accent2,
        // info: colors.blue,
        // success: colors.green,
        error: colors.red.accent2
      },
      dark: {
        background: colors.grey.darken3,
        primary: colors.grey.darken4,
        secondary: colors.grey.darken2,
        accent: colors.indigo.accent4,
        // info: colors.blue.darken2,
        // success: colors.green.darken2,
        error: colors.red.accent2
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
